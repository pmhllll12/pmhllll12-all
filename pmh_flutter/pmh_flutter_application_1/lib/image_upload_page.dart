/// 이미지를 골라 백엔드(`/api/admin/s3/images`)로 올리는 화면.
///
/// 서버 파이프라인은 라우터 → 유스케이스 → 포트 → S3 어댑터로 갈라져 있고,
/// 앱은 그중 **HTTP 계약만** 안다 — 버킷 이름도 presigned URL 만드는 방법도 모른다.
///
/// 업로드가 끝나면 서버가 1시간짜리 조회 URL을 돌려준다. 버킷은 비공개라
/// 그 URL 없이는 열리지 않는다.
library;

import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'package:image_picker/image_picker.dart';

import 'auth.dart';

/// 백엔드 주소. 인증 게이트웨이(`AUTH_BASE_URL`)와 다른 호스트다.
///
/// ```
/// flutter run --dart-define=API_BASE_URL=https://api.pmhllll12.cloud
/// ```
const apiBaseUrl = String.fromEnvironment('API_BASE_URL');

const _uploadTimeout = Duration(seconds: 60);

/// 확장자 → Content-Type.
///
/// multipart 파트에 Content-Type을 안 넣으면 `application/octet-stream`으로
/// 나가고, 서버가 허용 형식이 아니라며 422로 되돌린다.
const _contentTypeByExtension = <String, String>{
  'jpg': 'image/jpeg',
  'jpeg': 'image/jpeg',
  'png': 'image/png',
  'gif': 'image/gif',
  'webp': 'image/webp',
};

String? _contentTypeFor(XFile file) {
  final declared = file.mimeType;
  if (declared != null && _contentTypeByExtension.containsValue(declared)) {
    return declared;
  }
  final dotIndex = file.path.lastIndexOf('.');
  if (dotIndex < 0) return null;
  return _contentTypeByExtension[file.path.substring(dotIndex + 1).toLowerCase()];
}

/// 서버가 알려 준 업로드 제한. 앱에 같은 숫자를 복사해 두면 서버 정책이 바뀔 때
/// 조용히 어긋나므로, `/allowed-types` 로 받아 온다.
@immutable
class UploadLimits {
  const UploadLimits({required this.contentTypes, required this.maxBytes});

  final List<String> contentTypes;
  final int maxBytes;

  String get maxLabel => '${(maxBytes / (1024 * 1024)).round()}MB';
}

/// 업로드 결과. 서버 응답의 일부만 화면에서 쓴다.
@immutable
class UploadedImage {
  const UploadedImage({
    required this.key,
    required this.url,
    required this.sizeBytes,
    required this.contentType,
  });

  final String key;
  final String url;
  final int sizeBytes;
  final String contentType;
}

class ImageUploadPage extends StatefulWidget {
  const ImageUploadPage({super.key});

  @override
  State<ImageUploadPage> createState() => _ImageUploadPageState();
}

class _ImageUploadPageState extends State<ImageUploadPage> {
  final ImagePicker _picker = ImagePicker();

  XFile? _picked;
  UploadLimits? _limits;
  UploadedImage? _uploaded;
  String? _error;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _loadLimits();
  }

  Future<void> _loadLimits() async {
    if (apiBaseUrl.isEmpty) return;
    try {
      final response = await http
          .get(Uri.parse('$apiBaseUrl/api/admin/s3/images/allowed-types'))
          .timeout(const Duration(seconds: 10));
      if (response.statusCode != 200) return;
      final body = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      if (!mounted) return;
      setState(() {
        _limits = UploadLimits(
          contentTypes: (body['allowed_content_types'] as List<dynamic>).cast<String>(),
          maxBytes: body['max_bytes'] as int,
        );
      });
    } catch (error) {
      // 제한 안내를 못 받아도 업로드 자체는 된다 — 서버가 최종 판정을 한다.
      debugPrint('[upload] 업로드 제한 조회 실패: $error');
    }
  }

  Future<void> _pick(ImageSource source) async {
    if (_busy) return;
    try {
      final file = await _picker.pickImage(source: source);
      if (file == null || !mounted) return; // 사용자가 선택을 취소했다.
      setState(() {
        _picked = file;
        _uploaded = null;
        _error = null;
      });
    } catch (error) {
      debugPrint('[upload] 이미지 선택 실패: $error');
      if (!mounted) return;
      setState(() => _error = '이미지를 불러오지 못했습니다.');
    }
  }

  Future<void> _upload() async {
    final file = _picked;
    if (file == null || _busy) return;

    if (apiBaseUrl.isEmpty) {
      setState(() => _error = 'API 주소가 설정되지 않았습니다.\n--dart-define=API_BASE_URL=... 로 빌드하세요.');
      return;
    }

    final contentType = _contentTypeFor(file);
    if (contentType == null) {
      setState(() => _error = '지원하지 않는 형식입니다. JPEG·PNG·GIF·WEBP만 올릴 수 있습니다.');
      return;
    }

    setState(() {
      _busy = true;
      _error = null;
      _uploaded = null;
    });

    try {
      final bytes = await file.readAsBytes();
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$apiBaseUrl/api/admin/s3/images'),
      );
      // 이 엔드포인트는 아직 인증을 요구하지 않지만, 세션이 있으면 붙여 둔다 —
      // 서버에 인증을 걸 때 앱을 다시 배포하지 않아도 된다.
      final accessToken = await AuthService.instance.ensureAccessToken();
      if (accessToken != null) {
        request.headers['Authorization'] = 'Bearer $accessToken';
      }
      request.files.add(
        http.MultipartFile.fromBytes(
          'file',
          bytes,
          filename: file.name,
          contentType: MediaType.parse(contentType),
        ),
      );

      final streamed = await request.send().timeout(_uploadTimeout);
      final response = await http.Response.fromStream(streamed);
      if (!mounted) return;

      if (response.statusCode == 200) {
        final body = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
        setState(() {
          _busy = false;
          _uploaded = UploadedImage(
            key: body['key'] as String,
            url: body['url'] as String,
            sizeBytes: body['size_bytes'] as int,
            contentType: body['content_type'] as String,
          );
        });
        return;
      }

      setState(() {
        _busy = false;
        _error = _messageFor(response);
      });
    } catch (error) {
      debugPrint('[upload] 업로드 실패: $error');
      if (!mounted) return;
      setState(() {
        _busy = false;
        _error = '업로드 중 문제가 발생했습니다. 네트워크를 확인해 주세요.';
      });
    }
  }

  /// 서버는 실패 사유를 `detail`에 한국어로 담아 준다 — 그대로 보여주는 편이
  /// 앱에서 다시 문구를 만드는 것보다 정확하다.
  String _messageFor(http.Response response) {
    try {
      final body = jsonDecode(utf8.decode(response.bodyBytes)) as Map<String, dynamic>;
      final detail = body['detail'];
      if (detail is String && detail.isNotEmpty) return detail;
    } catch (_) {
      // 아래 기본 문구로 떨어진다.
    }
    return '업로드에 실패했습니다. (오류 ${response.statusCode})';
  }

  @override
  Widget build(BuildContext context) {
    final picked = _picked;
    final uploaded = _uploaded;

    return Scaffold(
      backgroundColor: _UpColors.bg0,
      appBar: AppBar(
        backgroundColor: _UpColors.bg1,
        foregroundColor: _UpColors.fg0,
        title: const Text('이미지 업로드'),
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
        children: [
          _PreviewBox(file: picked),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _SourceButton(
                  icon: Icons.photo_library_outlined,
                  label: '갤러리',
                  onPressed: _busy ? null : () => _pick(ImageSource.gallery),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _SourceButton(
                  icon: Icons.photo_camera_outlined,
                  label: '카메라',
                  onPressed: _busy ? null : () => _pick(ImageSource.camera),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _LimitsHint(limits: _limits),
          const SizedBox(height: 20),
          SizedBox(
            height: 52,
            child: ElevatedButton(
              onPressed: (picked == null || _busy) ? null : _upload,
              style: ElevatedButton.styleFrom(
                backgroundColor: _UpColors.accent,
                foregroundColor: const Color(0xFF04131A),
                disabledBackgroundColor: const Color(0x3322D3EE),
                disabledForegroundColor: _UpColors.fg2,
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: _busy
                  ? const SizedBox(
                      width: 22,
                      height: 22,
                      child: CircularProgressIndicator(strokeWidth: 2.4, color: Colors.black87),
                    )
                  : const Text(
                      'S3에 업로드',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                    ),
            ),
          ),
          if (_error != null) ...[
            const SizedBox(height: 20),
            _ErrorCard(message: _error!),
          ],
          if (uploaded != null) ...[
            const SizedBox(height: 20),
            _ResultCard(uploaded: uploaded),
          ],
        ],
      ),
    );
  }
}

class _PreviewBox extends StatelessWidget {
  const _PreviewBox({required this.file});

  final XFile? file;

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 4 / 3,
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: _UpColors.bg1,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: _UpColors.border),
        ),
        child: file == null
            ? const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.image_outlined, color: _UpColors.fg3, size: 40),
                    SizedBox(height: 10),
                    Text('이미지를 선택하세요', style: TextStyle(color: _UpColors.fg2, fontSize: 14)),
                  ],
                ),
              )
            : ClipRRect(
                borderRadius: BorderRadius.circular(13),
                child: Image.file(File(file!.path), fit: BoxFit.cover),
              ),
      ),
    );
  }
}

class _SourceButton extends StatelessWidget {
  const _SourceButton({required this.icon, required this.label, required this.onPressed});

  final IconData icon;
  final String label;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 48,
      child: OutlinedButton.icon(
        onPressed: onPressed,
        icon: Icon(icon, size: 18),
        label: Text(label),
        style: OutlinedButton.styleFrom(
          foregroundColor: _UpColors.fg0,
          side: const BorderSide(color: _UpColors.border),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        ),
      ),
    );
  }
}

class _LimitsHint extends StatelessWidget {
  const _LimitsHint({required this.limits});

  final UploadLimits? limits;

  @override
  Widget build(BuildContext context) {
    final value = limits;
    final text = value == null
        ? '서버에서 허용 형식을 불러오는 중입니다.'
        : '${value.contentTypes.map((t) => t.split('/').last.toUpperCase()).join(' · ')} · 최대 ${value.maxLabel}';
    return Text(
      text,
      textAlign: TextAlign.center,
      style: const TextStyle(color: _UpColors.fg3, fontSize: 12),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  const _ErrorCard({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: const Color(0x1AFF6B6B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0x4DFF6B6B)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Icon(Icons.error_outline, color: _UpColors.error, size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(color: _UpColors.error, fontSize: 13, height: 1.5),
            ),
          ),
        ],
      ),
    );
  }
}

/// 업로드 결과. 서버가 준 presigned URL로 이미지를 **다시 내려받아** 보여준다 —
/// 로컬 파일이 아니라 실제로 S3에 올라간 것을 확인하는 의미가 있다.
class _ResultCard extends StatelessWidget {
  const _ResultCard({required this.uploaded});

  final UploadedImage uploaded;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0x1A22D3EE),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0x4D22D3EE)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.check_circle_outline, color: _UpColors.accent, size: 18),
              SizedBox(width: 8),
              Text(
                '업로드 완료',
                style: TextStyle(
                  color: _UpColors.accent,
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(10),
            child: Image.network(
              uploaded.url,
              height: 160,
              width: double.infinity,
              fit: BoxFit.cover,
              errorBuilder: (_, _, _) => const SizedBox(
                height: 160,
                child: Center(
                  child: Text(
                    '조회 URL로 이미지를 불러오지 못했습니다.',
                    style: TextStyle(color: _UpColors.fg2, fontSize: 12),
                  ),
                ),
              ),
            ),
          ),
          const SizedBox(height: 12),
          _ResultRow(label: 'key', value: uploaded.key),
          _ResultRow(label: '형식', value: uploaded.contentType),
          _ResultRow(label: '크기', value: '${uploaded.sizeBytes} bytes'),
          const SizedBox(height: 8),
          const Text(
            '조회 URL은 1시간 뒤 만료됩니다. 버킷은 비공개라 URL 없이는 열리지 않습니다.',
            style: TextStyle(color: _UpColors.fg3, fontSize: 11, height: 1.5),
          ),
        ],
      ),
    );
  }
}

class _ResultRow extends StatelessWidget {
  const _ResultRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 44,
            child: Text(label, style: const TextStyle(color: _UpColors.fg3, fontSize: 12)),
          ),
          Expanded(
            child: Text(value, style: const TextStyle(color: _UpColors.fg1, fontSize: 12)),
          ),
        ],
      ),
    );
  }
}

class _UpColors {
  static const bg0 = Color(0xFF04070F);
  static const bg1 = Color(0xFF0A1020);
  static const fg0 = Color(0xFFFFFFFF);
  static const fg1 = Color(0xFFCBD5E1);
  static const fg2 = Color(0xFF94A3B8);
  static const fg3 = Color(0xFF64748B);
  static const accent = Color(0xFF22D3EE);
  static const border = Color(0x2E94A3B8);
  static const error = Color(0xFFFF6B6B);
}
