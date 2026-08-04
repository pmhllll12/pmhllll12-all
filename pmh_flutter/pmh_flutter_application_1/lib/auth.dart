/// 카카오 소셜 로그인 화면과 세션 관리.
///
/// 흐름은 `pmh_flutter/_docs/flutter-kakao-oauth-harness.md` 를 따른다.
///
/// ```
/// 인트로 영상 ──4초──> AuthPage ──카카오 로그인──> 백엔드 토큰 교환 ──> StopwatchPage
/// ```
///
/// 앱이 들고 다니는 자격증명은 **백엔드가 발급한 자체 JWT뿐**이다. 카카오
/// access token 은 백엔드로 한 번 넘긴 뒤 앱에서 보관하지 않고, 사용자 정보
/// 조회(`UserApi.instance.me()`)도 하지 않는다 — 카카오에 같은 조회가 두 번
/// 나가고 앱과 서버의 정보가 어긋날 수 있다.
library;

import 'dart:async';
import 'dart:convert';
import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:kakao_flutter_sdk_user/kakao_flutter_sdk_user.dart';

import 'stopwatch_page.dart';

/// 카카오 네이티브 앱키. 소스에 박지 않고 빌드 시 주입한다.
///
/// ```
/// flutter run \
///   --dart-define=KAKAO_NATIVE_APP_KEY=xxxx \
///   --dart-define=AUTH_BASE_URL=http://192.168.0.10:9000
/// ```
///
/// 안드로이드 매니페스트의 리다이렉트 스킴(`kakao<앱키>://oauth`)에도 같은 값이
/// 필요하다 — 그쪽은 `android/local.properties` 의 `kakao.nativeAppKey` 에서 읽는다.
/// **두 값이 다르면 카카오톡에서 앱으로 돌아오지 못한다.**
const kakaoNativeAppKey = String.fromEnvironment('KAKAO_NATIVE_APP_KEY');

/// 인증 게이트웨이 주소. `minho` 의 `auth` 컨테이너(:9000)를 가리킨다.
///
/// 실기기에서는 `localhost` 가 개발 PC를 가리키지 않는다 — PC의 LAN IP나
/// 터널 호스트를 넣어야 한다.
const authBaseUrl = String.fromEnvironment('AUTH_BASE_URL');

/// 백엔드 호출 한 건의 제한 시간. 카카오든 백엔드든 어느 쪽이 느려도 로그인
/// 버튼이 영원히 도는 것은 막는다.
const _requestTimeout = Duration(seconds: 15);

// ---------------------------------------------------------------------------
// 예외
// ---------------------------------------------------------------------------

/// 로그인 실패. [message] 는 그대로 사용자에게 보여줄 수 있는 한국어 문장이다.
class AuthException implements Exception {
  const AuthException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => 'AuthException(${statusCode ?? '-'}): $message';
}

/// 사용자가 카카오 로그인 창을 스스로 닫았다. **에러가 아니다** — 화면에
/// 빨간 문구를 띄우지 말고 조용히 원래 상태로 돌아간다.
class AuthCancelledException implements Exception {
  const AuthCancelledException();

  @override
  String toString() => 'AuthCancelledException';
}

// ---------------------------------------------------------------------------
// 세션
// ---------------------------------------------------------------------------

/// 발급받은 자체 JWT 한 쌍.
@immutable
class AuthTokens {
  const AuthTokens({required this.accessToken, required this.refreshToken});

  final String accessToken;
  final String refreshToken;
}

/// JWT 페이로드의 `exp` 를 읽는다. 서명은 검증하지 않는다 — 만료 시각을 미리
/// 알아 불필요한 401 왕복을 줄이려는 용도일 뿐, 신뢰 판단은 서버가 한다.
DateTime? _jwtExpiry(String jwt) {
  final parts = jwt.split('.');
  if (parts.length != 3) return null;
  try {
    final payload = utf8.decode(base64Url.decode(base64Url.normalize(parts[1])));
    final exp = (jsonDecode(payload) as Map<String, dynamic>)['exp'];
    if (exp is! int) return null;
    return DateTime.fromMillisecondsSinceEpoch(exp * 1000, isUtc: true);
  } catch (_) {
    return null;
  }
}

/// UUID v4. `uuid` 패키지를 하나 더 받지 않으려고 직접 만든다.
///
/// 안드로이드 ID·광고 ID 같은 기기 식별자를 쓰지 않는 이유는 스토어 정책과
/// 초기화 시 값이 바뀌는 문제 때문이다.
String _newDeviceId() {
  final random = Random.secure();
  final bytes = List<int>.generate(16, (_) => random.nextInt(256));
  bytes[6] = (bytes[6] & 0x0f) | 0x40; // version 4
  bytes[8] = (bytes[8] & 0x3f) | 0x80; // variant 10xx
  final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
  return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-'
      '${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
}

/// 카카오 로그인 + 자체 JWT 세션을 관리한다.
///
/// 백엔드의 모바일 세션 키는 `authgw:mobile:refresh:{sub}:{device_id}` 이므로
/// [deviceId] 가 매번 바뀌면 로그인할 때마다 Redis 에 좀비 세션이 쌓인다.
/// 그래서 device_id 는 최초 1회만 만들고 **로그아웃해도 지우지 않는다.**
class AuthService {
  AuthService._();

  static final AuthService instance = AuthService._();

  static const _storage = FlutterSecureStorage();
  static const _keyAccess = 'auth.access_token';
  static const _keyRefresh = 'auth.refresh_token';
  static const _keyDeviceId = 'auth.device_id';
  static const _deviceIdHeader = 'X-Device-Id';

  /// 동시에 여러 곳에서 갱신을 부르면 백엔드의 리프레시 회전이 경합해 서로의
  /// 토큰을 무효화한다. 진행 중인 갱신이 있으면 그 Future 를 함께 기다린다.
  Future<String?>? _refreshInFlight;

  /// 이 기기의 고정 식별자. 없으면 만들어 저장한다.
  Future<String> deviceId() async {
    final stored = await _storage.read(key: _keyDeviceId);
    if (stored != null && stored.isNotEmpty) return stored;

    final created = _newDeviceId();
    await _storage.write(key: _keyDeviceId, value: created);
    return created;
  }

  /// 인트로·로그인 화면을 건너뛰어도 되는지 판단한다.
  ///
  /// 로컬에 남은 리프레시 토큰의 만료 시각만 본다 — 서버에 물어보면 정확하지만
  /// 앱 시작이 네트워크 왕복만큼 늦어진다. 서버가 이미 세션을 폐기했다면 이후
  /// 첫 갱신이 실패하면서 [_clearSession] 으로 정리된다.
  Future<bool> hasStoredSession() async {
    final refreshToken = await _storage.read(key: _keyRefresh);
    if (refreshToken == null || refreshToken.isEmpty) return false;

    final expiry = _jwtExpiry(refreshToken);
    if (expiry == null) return false;
    return expiry.isAfter(DateTime.now().toUtc());
  }

  /// 카카오 로그인 → 백엔드 토큰 교환 → 세션 저장까지 한 번에 수행한다.
  ///
  /// 사용자가 창을 닫으면 [AuthCancelledException], 그 밖의 실패는
  /// [AuthException] 을 던진다.
  Future<void> loginWithKakao() async {
    if (authBaseUrl.isEmpty) {
      throw const AuthException(
        '인증 서버 주소가 설정되지 않았습니다.\n'
        '--dart-define=AUTH_BASE_URL=... 로 빌드하세요.',
      );
    }

    final kakaoToken = await _kakaoLogin();
    final tokens = await _exchangeWithBackend(kakaoToken);

    await _storage.write(key: _keyAccess, value: tokens.accessToken);
    await _storage.write(key: _keyRefresh, value: tokens.refreshToken);
  }

  /// 카카오 SDK 로그인. 카카오톡이 깔려 있으면 앱 전환, 아니면 카카오계정
  /// 웹 로그인을 쓴다 (developers.kakao.com 의 Flutter 가이드 패턴).
  Future<OAuthToken> _kakaoLogin() async {
    if (await isKakaoTalkInstalled()) {
      try {
        final token = await UserApi.instance.loginWithKakaoTalk();
        debugPrint('[auth] 카카오톡으로 로그인 성공');
        return token;
      } catch (error) {
        debugPrint('[auth] 카카오톡으로 로그인 실패: $error');
        // 사용자가 직접 닫은 경우다. 여기서 카카오계정 로그인으로 넘어가면
        // 방금 취소한 사용자에게 로그인 창을 다시 들이미는 꼴이 된다.
        if (error is PlatformException && error.code == 'CANCELED') {
          throw const AuthCancelledException();
        }
        // 그 밖의 실패(카카오톡에 로그인돼 있지 않은 경우 등)는 아래 카카오계정
        // 로그인으로 폴백한다.
      }
    }

    try {
      final token = await UserApi.instance.loginWithKakaoAccount();
      debugPrint('[auth] 카카오계정으로 로그인 성공');
      return token;
    } catch (error) {
      debugPrint('[auth] 카카오계정으로 로그인 실패: $error');
      if (error is PlatformException && error.code == 'CANCELED') {
        throw const AuthCancelledException();
      }
      throw const AuthException('카카오 로그인에 실패했습니다. 다시 시도해 주세요.');
    }
  }

  /// 카카오 토큰을 백엔드로 넘겨 자체 JWT 를 받는다.
  ///
  /// 백엔드는 이 요청을 받아 카카오에 토큰을 검증하고, 발급한 리프레시 토큰을
  /// Redis 모바일 세션 해시(`authgw:mobile:refresh:{sub}:{device_id}`)에
  /// 기록한다. 그래서 [_deviceIdHeader] 가 없으면 400 이다.
  Future<AuthTokens> _exchangeWithBackend(OAuthToken kakaoToken) async {
    final body = <String, String>{'access_token': kakaoToken.accessToken};
    // OpenID Connect 를 켠 앱이면 id_token 도 함께 보낸다. 백엔드가 카카오
    // JWKS 로 로컬 검증할 수 있어 카카오 API 왕복이 사라진다.
    final idToken = kakaoToken.idToken;
    if (idToken != null && idToken.isNotEmpty) {
      body['id_token'] = idToken;
    }

    return _tokensFrom(await _post('/auth/kakao/mobile', body));
  }

  /// 유효한 access token 을 돌려준다. 만료가 임박했으면 갱신하고, 세션이
  /// 끊겼으면 저장소를 비운 뒤 `null` 을 돌려준다.
  ///
  /// 앞으로 백엔드 API 를 호출하는 화면은 이 메서드로 토큰을 얻는다.
  Future<String?> ensureAccessToken() async {
    final accessToken = await _storage.read(key: _keyAccess);
    if (accessToken != null && accessToken.isNotEmpty) {
      final expiry = _jwtExpiry(accessToken);
      // 만료 30초 전부터 미리 갱신한다 — 요청이 날아가는 사이 만료되는 것을 피한다.
      final safeUntil = DateTime.now().toUtc().add(const Duration(seconds: 30));
      if (expiry != null && expiry.isAfter(safeUntil)) return accessToken;
    }
    return _refreshInFlight ??= _refresh().whenComplete(() {
      _refreshInFlight = null;
    });
  }

  Future<String?> _refresh() async {
    final refreshToken = await _storage.read(key: _keyRefresh);
    if (refreshToken == null || refreshToken.isEmpty) return null;

    try {
      final tokens = _tokensFrom(
        await _post('/auth/mobile/refresh', {'refresh_token': refreshToken}),
      );
      // 리프레시는 **회전한다.** 새 값으로 덮어쓰지 않고 옛 토큰을 다시 보내면
      // 백엔드가 탈취로 간주해 세션을 끊는다.
      await _storage.write(key: _keyAccess, value: tokens.accessToken);
      await _storage.write(key: _keyRefresh, value: tokens.refreshToken);
      return tokens.accessToken;
    } on AuthException catch (error) {
      debugPrint('[auth] 세션 갱신 실패: $error');
      await _clearSession();
      return null;
    }
  }

  /// 로그아웃. [allDevices] 가 참이면 이 계정의 **모든 모바일 기기** 세션을
  /// 지운다. 어느 쪽이든 웹 세션에는 영향이 없다 — 설계상 의도된 동작이다.
  Future<void> logout({bool allDevices = false}) async {
    final accessToken = await _storage.read(key: _keyAccess);
    if (accessToken != null && accessToken.isNotEmpty) {
      try {
        await _post(
          allDevices ? '/auth/mobile/logout-all' : '/auth/mobile/logout',
          const <String, String>{},
          bearer: accessToken,
        );
      } on AuthException catch (error) {
        // 서버 세션이 이미 없어도 로컬 정리는 진행해야 한다.
        debugPrint('[auth] 서버 로그아웃 건너뜀: $error');
      }
    }

    try {
      await UserApi.instance.logout();
      debugPrint('[auth] 카카오 SDK 토큰 폐기');
    } catch (error) {
      debugPrint('[auth] 카카오 SDK 로그아웃 실패: $error');
    }

    await _clearSession();
  }

  /// device_id 는 남긴다 — 같은 기기가 같은 세션 슬롯을 다시 쓰게 해야
  /// Redis 에 쓰지 않는 키가 쌓이지 않는다.
  Future<void> _clearSession() async {
    await _storage.delete(key: _keyAccess);
    await _storage.delete(key: _keyRefresh);
  }

  Future<Map<String, dynamic>> _post(
    String path,
    Map<String, String> body, {
    String? bearer,
  }) async {
    final headers = <String, String>{
      'Content-Type': 'application/json',
      _deviceIdHeader: await deviceId(),
      if (bearer != null) 'Authorization': 'Bearer $bearer',
    };

    final http.Response response;
    try {
      response = await http
          .post(
            Uri.parse('$authBaseUrl$path'),
            headers: headers,
            body: jsonEncode(body),
          )
          .timeout(_requestTimeout);
    } on TimeoutException {
      throw const AuthException('인증 서버가 응답하지 않습니다. 잠시 후 다시 시도해 주세요.');
    } catch (error) {
      debugPrint('[auth] $path 요청 실패: $error');
      throw const AuthException('네트워크에 연결할 수 없습니다.');
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw AuthException(
        _messageFor(response.statusCode),
        statusCode: response.statusCode,
      );
    }

    // 로그아웃처럼 본문이 없는 응답도 있다. 토큰이 필요한 쪽은 _tokensFrom 이
    // 형식을 검사하므로 여기서는 빈 맵을 돌려줘도 안전하다.
    if (response.bodyBytes.isEmpty) return const <String, dynamic>{};
    try {
      return jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
    } catch (error) {
      debugPrint('[auth] $path 응답 해석 실패: $error');
      throw const AuthException('인증 서버 응답 형식이 올바르지 않습니다.');
    }
  }

  /// 백엔드 명세(하네스 문서 §5.1)의 상태 코드 → 사용자 문구.
  String _messageFor(int statusCode) {
    switch (statusCode) {
      case 400:
        // 기기 식별자가 빠진 경우다. 사용자가 재시도해도 달라지지 않는다.
        return '앱 설정 오류로 로그인할 수 없습니다. 앱을 다시 설치해 주세요.';
      case 401:
        return '로그인 정보가 만료되었습니다. 다시 로그인해 주세요.';
      case 403:
        return '이메일 제공에 동의해야 가입할 수 있습니다.';
      case 502:
        return '카카오 서버와 통신할 수 없습니다. 잠시 후 다시 시도해 주세요.';
      default:
        return '로그인에 실패했습니다. (오류 $statusCode)';
    }
  }

  AuthTokens _tokensFrom(Map<String, dynamic> body) {
    final accessToken = body['access_token'];
    final refreshToken = body['refresh_token'];
    if (accessToken is! String || refreshToken is! String) {
      throw const AuthException('인증 서버 응답 형식이 올바르지 않습니다.');
    }
    return AuthTokens(accessToken: accessToken, refreshToken: refreshToken);
  }
}

// ---------------------------------------------------------------------------
// 화면
// ---------------------------------------------------------------------------

/// 앱 팔레트(`main.dart` 의 `AppColors`)와 카카오 브랜드 색.
class _AuthColors {
  static const bg0 = Color(0xFF04070F);
  static const bg1 = Color(0xFF0A1020);
  static const fg0 = Color(0xFFFFFFFF);
  static const fg2 = Color(0xFF94A3B8);
  static const error = Color(0xFFFF6B6B);

  /// 카카오 디자인 가이드가 정한 값 — 임의로 바꾸지 않는다.
  static const kakaoYellow = Color(0xFFFEE500);
  static const kakaoLabel = Color(0xD9000000); // 검정 85%
}

/// 카카오 로그인 화면. 인트로 영상이 끝나면 여기로 온다.
class AuthPage extends StatefulWidget {
  const AuthPage({super.key});

  @override
  State<AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<AuthPage> {
  bool _busy = false;
  String? _error;

  Future<void> _login() async {
    if (_busy) return;
    setState(() {
      _busy = true;
      _error = null;
    });

    try {
      await AuthService.instance.loginWithKakao();
      if (!mounted) return;
      Navigator.of(context).pushReplacement(
        MaterialPageRoute<void>(builder: (_) => const StopwatchPage()),
      );
    } on AuthCancelledException {
      // 사용자가 스스로 닫았다. 버튼만 되살리고 아무 말도 하지 않는다.
      if (!mounted) return;
      setState(() => _busy = false);
    } on AuthException catch (error) {
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = error.message;
      });
    } catch (error) {
      debugPrint('[auth] 예상하지 못한 로그인 오류: $error');
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = '로그인 중 문제가 발생했습니다. 다시 시도해 주세요.';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _AuthColors.bg0,
      body: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [_AuthColors.bg1, _AuthColors.bg0],
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 28),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Spacer(flex: 3),
                const Text(
                  'WORLDCUP',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: _AuthColors.fg0,
                    fontWeight: FontWeight.w800,
                    fontSize: 28,
                    letterSpacing: 6,
                  ),
                ),
                const SizedBox(height: 14),
                const Text(
                  '카카오 계정으로 시작하세요',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: _AuthColors.fg2,
                    fontSize: 15,
                    height: 1.6,
                  ),
                ),
                const Spacer(flex: 4),
                _ErrorBanner(message: _error),
                _KakaoLoginButton(busy: _busy, onPressed: _login),
                const SizedBox(height: 20),
                const Text(
                  '로그인하면 서비스 이용약관과 개인정보 처리방침에 동의하게 됩니다.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: _AuthColors.fg2,
                    fontSize: 12,
                    height: 1.6,
                  ),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  const _ErrorBanner({required this.message});

  final String? message;

  @override
  Widget build(BuildContext context) {
    final text = message;
    if (text == null) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: const Color(0x1AFF6B6B),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0x4DFF6B6B)),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.error_outline, color: _AuthColors.error, size: 18),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                text,
                style: const TextStyle(
                  color: _AuthColors.error,
                  fontSize: 13,
                  height: 1.5,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// 카카오 로그인 버튼.
///
/// 노란 배경(#FEE500)과 검정 85% 글자는 카카오 디자인 가이드가 정한 값이다.
/// 아이콘은 임시다 — 배포 전 카카오가 제공하는 공식 심볼 이미지로 교체한다.
class _KakaoLoginButton extends StatelessWidget {
  const _KakaoLoginButton({required this.busy, required this.onPressed});

  final bool busy;
  final VoidCallback onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 54,
      child: ElevatedButton(
        onPressed: busy ? null : onPressed,
        style: ElevatedButton.styleFrom(
          backgroundColor: _AuthColors.kakaoYellow,
          foregroundColor: _AuthColors.kakaoLabel,
          disabledBackgroundColor: const Color(0x66FEE500),
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: busy
            ? const SizedBox(
                width: 22,
                height: 22,
                child: CircularProgressIndicator(
                  strokeWidth: 2.4,
                  color: _AuthColors.kakaoLabel,
                ),
              )
            : const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.chat_bubble, size: 19),
                  SizedBox(width: 10),
                  Text(
                    '카카오로 로그인',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                  ),
                ],
              ),
      ),
    );
  }
}
