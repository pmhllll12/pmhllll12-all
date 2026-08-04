# 카카오 소셜 로그인 — 플러터 하네스

`pmh_flutter_application_1`에서 카카오 로그인을 붙이는 절차. **클라이언트 쪽만** 다룬다.
토큰 검증·세션 저장·JWT 발급은 백엔드 몫이다.

백엔드 쪽 지시서 ---> [`../../minho/_docs/flutter-kakao-oauth-harmess.md`](../../minho/_docs/flutter-kakao-oauth-harmess.md)
실기기 연동 ---> [`flutter-android-harness.md`](flutter-android-harness.md)
린트/포맷 ---> [`linting.md`](linting.md)
플러터 영역 지침 ---> [`../CLAUDE.md`](../CLAUDE.md)

> 이 문서는 **구현 지시서**다. 아직 코드도 의존성도 없다. §1에서 현재 상태를 확인하고,
> §8 미결 질문은 추측하지 말고 확정한 뒤 착수한다.

---

## 0. 역할 경계 — 앱이 하는 일 / 하지 않는 일

```
[앱]  카카오 SDK로 로그인 → access_token (+ id_token) 획득
[앱]  그 토큰을 백엔드로 1회 전송
[앱]  돌려받은 자체 JWT 쌍을 secure storage에 보관하고 이후 API 호출에 붙임
```

**앱이 하지 않는 것:**

- `UserApi.instance.me()` 호출 — 사용자 정보는 **백엔드가 카카오에 물어본다.**
  앱에서 또 부르면 같은 조회가 두 번 나가고, 두 곳의 정보가 어긋날 수 있다.
- 카카오 토큰을 저장·재사용 — 백엔드에 넘긴 뒤에는 버린다. 앱이 들고 다니는 자격증명은
  **자체 JWT뿐**이다. (카카오 SDK가 내부 토큰 저장소에 보관하는 것은 SDK 소관이며,
  앱 코드가 직접 꺼내 쓰지 않는다.)
- 카카오 REST 앱키·Client Secret 보관 — 앱에 들어가는 건 **네이티브 앱키**뿐이다.
  네이티브 앱키는 리버싱으로 노출되는 걸 전제로 설계된 값이라 앱에 넣어도 된다.
  **REST 앱키·Client Secret은 절대 앱에 넣지 않는다.**

---

## 1. 현재 저장소 상태

문서와 코드가 어긋나면 **코드가 정본**이다. (2026-08-03 확인)

| 항목 | 값 | 출처 |
|---|---|---|
| Dart SDK | `^3.12.2` | [`pubspec.yaml`](../pmh_flutter_application_1/pubspec.yaml) |
| `applicationId` / `namespace` | `com.pmhllll12.pmh_flutter_application_1` | `android/app/build.gradle.kts` |
| `minSdk` | `flutter.minSdkVersion` 위임 (Flutter 3.44 → 24) | 같은 파일. **직접 숫자를 박지 않는다** |
| 인증 관련 의존성 | **없음** — `cupertino_icons`, `video_player`뿐 | `pubspec.yaml` |
| `lib/` 구조 | 평면 — `main.dart`, `counter_page.dart`, `stopwatch_page.dart`, `intro_video_page.dart`, `chat_page.dart` | |
| Android 매니페스트 | `MainActivity` 하나, 커스텀 스킴·`<queries>` 없음, `INTERNET` 권한 명시 없음 | `android/app/src/main/AndroidManifest.xml` |
| iOS | 하네스 문서가 **비어 있음** ([`flutter-iphone-harness.md`](flutter-iphone-harness.md)) | |

즉 **의존성·매니페스트·저장소·API 클라이언트가 전부 신규 작업**이다.

> `analysis_options.yaml`에 `avoid_print`가 켜져 있다. 로그인 흐름 디버깅에
> `print`를 쓰면 `dart analyze`가 막는다 — `debugPrint` 또는 `dart:developer`의
> `log`를 쓴다. **토큰 값 자체는 어떤 로그에도 찍지 않는다.**

---

## 2. 사전 준비 — 카카오 개발자 콘솔

코드보다 먼저 끝내야 한다. 여기서 나온 값이 §3·§4의 입력이다.

1. [Kakao Developers](https://developers.kakao.com)에서 앱 생성.
2. **앱 키** 확인 — 네이티브 앱키(앱용) / REST API 키(백엔드용)를 구분해 적어 둔다.
3. **플랫폼 등록**
   - Android: 패키지명 `com.pmhllll12.pmh_flutter_application_1` +
     **키 해시**(디버그 키스토어·릴리스 키스토어 **각각** 등록. 디버그만 등록하면
     릴리스 빌드에서 로그인이 실패한다).
   - iOS: 번들 ID (§8-Q3에서 확정).
4. **카카오 로그인 활성화** ON.
5. **동의항목** — 최소 `이메일`. 백엔드가 `sub`를 이메일로 잡고 있어(백엔드 문서 §6-Q1)
   이메일 동의가 없으면 로그인이 **403 `no_email`** 로 떨어진다. 선택 동의로 두면
   사용자가 거부할 수 있으므로 **필수 동의**로 설정할지 §8-Q1에서 정한다.
6. **OpenID Connect** ON/OFF — 켜면 `id_token`을 받아 백엔드가 네트워크 호출 없이
   로컬 검증할 수 있다. 백엔드 문서 §6-Q4와 **같은 답**이어야 한다.

키 해시 얻기(디버그):

```bash
keytool -exportcert -alias androiddebugkey -keystore ~/.android/debug.keystore \
  -storepass android -keypass android | openssl sha1 -binary | openssl base64
```

---

## 3. 의존성

`pubspec.yaml`에 추가한다. 버전은 착수 시점 최신 안정판을 `flutter pub add`로 잡는다.

| 패키지 | 용도 | 비고 |
|---|---|---|
| `kakao_flutter_sdk_user` | 카카오 로그인 | 전체 번들(`kakao_flutter_sdk`)이 아니라 **user 모듈만** 받는다. 지도·메시지는 쓰지 않는다. `KakaoSdk`·`OAuthToken`·`isKakaoTalkInstalled`는 이 패키지가 common/auth를 재수출해 함께 딸려 온다 |
| `flutter_secure_storage` | JWT·`device_id` 보관 | Android Keystore / iOS Keychain |
| `http` | 백엔드 호출 | 인증 4개 엔드포인트뿐이라 `dio` 인터셉터까지 갈 이유가 없다. 갱신 합치기는 `AuthService`가 Future 하나를 공유해 직접 처리한다 |
| `device_info_plus` | 기기 모델명(`X-Device-Model`) | **받지 않았다.** 선택 헤더라 의존성 하나를 아꼈다 — 기기 목록 UI를 만들 때 추가한다 |

```bash
cd pmh_flutter/pmh_flutter_application_1
flutter pub add kakao_flutter_sdk_user flutter_secure_storage http
```

> `shared_preferences`에 토큰을 넣지 않는다. 루팅·백업 경로로 평문 노출된다.

---

## 4. 플랫폼 설정

### 4.1 Android

**(a) `AndroidManifest.xml`** — `<manifest>` 바로 아래에 인터넷 권한을 추가한다.

```xml
<uses-permission android:name="android.permission.INTERNET"/>
```

**(b) 카카오계정(웹) 로그인 리다이렉트 수신** — `<application>` 안에 액티비티를 추가한다.
`${KAKAO_NATIVE_APP_KEY}`는 (c)에서 주입한다.

```xml
<activity
    android:name="com.kakao.sdk.flutter.auth.AuthCodeHandlerActivity"
    android:exported="true">
    <intent-filter android:label="flutter_web_auth">
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="kakao${KAKAO_NATIVE_APP_KEY}" android:host="oauth"/>
    </intent-filter>
</activity>
```

**(c) 앱키 주입** — 하드코딩하지 않는다. `android/app/build.gradle.kts`의
`defaultConfig`에서 `manifestPlaceholders`로 넣고, 값은 `local.properties`
(git 미추적)나 CI 시크릿에서 읽는다.

```kotlin
manifestPlaceholders["KAKAO_NATIVE_APP_KEY"] = kakaoNativeAppKey
```

**(d) 패키지 가시성**(Android 11+) — 카카오톡 설치 여부를 SDK가 조회하려면
기존 `<queries>` 블록에 추가한다. 없으면 항상 카카오계정(웹) 로그인으로 떨어진다.

```xml
<package android:name="com.kakao.talk"/>
```

**(e) 개발 중 평문 HTTP** — 백엔드를 `http://<PC LAN IP>:9000`으로 직접 부르면
Android 9+ 기본 정책이 차단한다. `network_security_config.xml`로 **개발 빌드에서만**
해당 호스트를 예외 처리한다. `android:usesCleartextTraffic="true"`를 매니페스트에
통째로 켜지 않는다 — 릴리스까지 따라간다.

### 4.2 iOS

`ios/Runner/Info.plist`:

```xml
<key>CFBundleURLTypes</key>
<array>
  <dict>
    <key>CFBundleURLSchemes</key>
    <array><string>kakao{NATIVE_APP_KEY}</string></array>
  </dict>
</array>
<key>LSApplicationQueriesSchemes</key>
<array>
  <string>kakaokompassauth</string>
  <string>kakaolink</string>
</array>
```

`LSApplicationQueriesSchemes`가 없으면 카카오톡이 깔려 있어도 앱 전환이 안 되고
웹 로그인으로 폴백한다.

### 4.3 `main.dart` 초기화

`runApp` 이전에 한 번:

```dart
KakaoSdk.init(nativeAppKey: <컴파일 타임 주입값>);
```

- 앱키는 `--dart-define=KAKAO_NATIVE_APP_KEY=...` + `String.fromEnvironment`로 받는다.
  소스에 리터럴로 박지 않는다(안드로이드는 §4.1(c)와 값이 같아야 한다).
- `WidgetsFlutterBinding.ensureInitialized()`가 먼저 와야 한다.

---

## 5. 로그인 흐름

```
1. 카카오톡 설치 여부 확인 → 설치돼 있으면 loginWithKakaoTalk(), 아니면 loginWithKakaoAccount()
   ※ 카카오톡 로그인은 사용자가 취소하면 예외가 난다 → 카카오계정 로그인으로 폴백
2. OAuthToken.accessToken (OIDC 켰으면 idToken)만 꺼낸다
3. device_id 로드(없으면 생성·저장) → §6
4. POST {AUTH_BASE_URL}/auth/kakao/mobile
     Header: X-Device-Id, X-Device-Model(선택)
     Body:   {"access_token": "..."} 또는 {"id_token": "..."}
5. 200이면 access/refresh JWT를 secure storage에 저장 → 홈 화면 이동
```

- **`UserApi.instance.me()`를 부르지 않는다** (§0).
- 카카오톡 앱 로그인 취소는 정상 흐름이다. `KakaoSdk`가 던지는
  `PlatformException(code: 'CANCELED')`을 에러로 표시하지 말고 폴백 처리한다.

### 5.1 백엔드 응답 처리

| 상태 | 의미 | 앱 동작 |
|---|---|---|
| 200 | 발급 성공 | 토큰 저장 → 홈 이동 |
| 400 | `X-Device-Id` 누락 등 | **앱 버그**다. 사용자에게 재시도를 시키지 말고 로그를 남긴다 |
| 401 | 카카오 토큰 검증 실패 | 카카오 로그아웃 후 처음부터 재시도 |
| 403 | 이메일 동의 없음(`no_email`) | "이메일 제공에 동의해야 가입할 수 있습니다" 안내 |
| 502 | 카카오 API 장애 | "잠시 후 다시 시도" — 재시도 버튼 |

### 5.2 자체 JWT 갱신

access JWT 수명은 **10분**, refresh는 14일(백엔드 문서 §1.1)이다. 앱은:

- API 호출이 401이면 `POST /auth/mobile/refresh` (Header `X-Device-Id`,
  Body `{"refresh_token": ...}`) → 새 쌍을 저장 → 원 요청 1회 재시도.
- **refresh는 회전한다.** 응답의 새 refresh_token으로 반드시 덮어쓴다. 옛 값을
  다시 보내면 백엔드가 탈취로 간주해 세션을 끊는다.
- 재발급까지 401이면 저장소를 비우고 로그인 화면으로 보낸다.
- **동시 401을 한 번의 refresh로 합쳐야 한다.** 여러 요청이 각자 refresh를 부르면
  회전 경합으로 서로의 토큰을 무효화한다 — 갱신 중이면 나머지는 그 Future를 기다린다.

### 5.3 로그아웃

- `POST /auth/mobile/logout` (해당 기기만) 또는 `/auth/mobile/logout-all` (모든 기기).
- 이어서 카카오 SDK `UserApi.instance.logout()`, secure storage 삭제.
- **`device_id`는 지우지 않는다** (§6).
- 웹 세션은 영향받지 않는다 — 설계상 의도된 동작이다(백엔드 문서 §9).

---

## 6. `device_id` — 모바일 세션의 키

백엔드는 `authgw:mobile:refresh:{sub}:{device_id}` 로 세션을 나눈다. 이 값이 매번
바뀌면 **로그인할 때마다 새 세션이 쌓이고 Redis에 좀비 키가 남는다.**

- 최초 실행 시 **UUID v4를 한 번 생성**해 `flutter_secure_storage`에 저장하고,
  이후 계속 그 값을 읽어 쓴다.
- **로그아웃해도 지우지 않는다.** 앱 삭제·재설치 시에만 새로 발급되는 게 맞다.
  (단 iOS Keychain은 앱 삭제 후에도 값이 남을 수 있다 — 그래도 무해하다.
  같은 기기가 같은 세션 슬롯을 재사용할 뿐이다.)
- `androidId`·IDFA 같은 **기기 식별자를 쓰지 않는다.** 스토어 정책 위반 소지가 있고
  초기화 시 값이 바뀐다.
- `X-Device-Model`(선택)은 `device_info_plus`로 얻어 넣는다 — 사용자가 "어느 기기에서
  로그인 중인지" 볼 수 있게 하는 용도이지, 인증에는 쓰이지 않는다.

---

## 7. 파일 배치

`lib/`는 화면 파일만 있는 평면 구조다. 인증도 그 결을 따라 **파일 하나**에 담았다.

```
lib/
├── main.dart            # KakaoSdk.init + 세션 유무로 시작 화면 결정
├── intro_video_page.dart# 4초 뒤 AuthPage 로 (기존 ChatPage 에서 변경)
├── auth.dart            # AuthService(세션·API) + AuthPage(로그인 화면)
└── stopwatch_page.dart  # 로그인 후 도착 지점
```

`auth.dart` 안의 구성:

| 심볼 | 역할 |
|---|---|
| `kakaoNativeAppKey` / `authBaseUrl` | `--dart-define` 으로 주입되는 빌드 상수 |
| `AuthException` / `AuthCancelledException` | 실패와 **사용자 취소**를 구분한다. 취소는 에러로 표시하지 않는다 |
| `AuthService` (싱글턴) | `deviceId()`, `hasStoredSession()`, `loginWithKakao()`, `ensureAccessToken()`, `logout()` |
| `AuthPage` | 카카오 로그인 버튼·오류 배너·진행 표시 |

- 백엔드 주소는 `--dart-define=AUTH_BASE_URL=...`로 주입한다.
  실기기는 `localhost`로 PC에 닿지 못한다 — PC의 LAN IP나 터널 호스트를 쓴다
  (실기기 연결 자체는 [`flutter-android-harness.md`](flutter-android-harness.md)).
- 화면이 커지면 `AuthService`를 `lib/auth/` 폴더로 쪼갠다. 지금 나누면 파일만
  늘고 얻는 게 없다.

---

## 8. 착수 전 확인할 미결 질문

- **Q1. 이메일을 필수 동의로 받을 것인가?**
  백엔드가 `sub`를 이메일로 잡고 있어 이메일이 없으면 로그인 자체가 불가능하다.
  선택 동의로 두면 403 안내 화면이 반드시 필요하다. 백엔드 문서 §6-Q1이 (b)안
  (users 테이블 + `kakao_id` 키)으로 바뀌면 이 제약은 사라진다.
- ~~**Q2. HTTP 클라이언트는 `dio`인가 `http`인가?**~~ → **`http` 로 정했다.**
  인증 엔드포인트 4개뿐이라 인터셉터가 필요 없고, 동시 갱신 합치기는
  `AuthService._refreshInFlight` 가 Future 하나를 공유하는 방식으로 처리한다.
- **Q3. iOS를 이번 범위에 넣는가?**
  넣는다면 번들 ID를 확정하고 카카오 콘솔에 등록해야 한다.
  ([`flutter-iphone-harness.md`](flutter-iphone-harness.md)가 아직 비어 있다.)
  **§4.2의 `Info.plist` 설정은 아직 적용하지 않았다** — 앱키를 plist에 문자열로
  박아야 해서(안드로이드처럼 gradle 플레이스홀더를 쓸 수 없다) 값이 정해진 뒤에
  넣는 게 맞다. iOS 빌드는 현재 카카오 로그인이 동작하지 않는다.
- **Q4. OIDC(`id_token`)를 쓰는가?**
  백엔드 문서 §6-Q4와 **같은 답**이어야 한다. 앱은 어느 쪽이든 코드량 차이가 거의
  없지만(꺼내는 필드만 다름), 서버 검증 경로가 완전히 갈린다.

---

## 9. 작업 순서

- [x] `pubspec.yaml` 의존성 추가 (§3) — `flutter pub get` 은 아직 돌리지 않았다
- [x] Android 매니페스트·gradle placeholder·`<queries>`·network security config (§4.1)
- [x] `main.dart` 에 `KakaoSdk.init` + 세션 게이트 (§4.3)
- [x] `auth.dart` — 저장소·`device_id`·카카오 폴백 로그인·백엔드 교환·갱신·로그아웃
- [x] `intro_video_page.dart` 가 `AuthPage` 로 넘어가도록 변경
- [ ] §8 미결 질문 확정 + §2 카카오 콘솔 설정 (키 해시 디버그·릴리스 **둘 다**)
- [ ] `android/local.properties` 에 `kakao.nativeAppKey=...` 기입
- [ ] **백엔드 `/auth/kakao/mobile` 등 4개 엔드포인트 구현**
      ([`../../minho/_docs/flutter-kakao-oauth-harmess.md`](../../minho/_docs/flutter-kakao-oauth-harmess.md))
      — 아직 없어서 로그인 요청은 실패한다
- [ ] iOS `Info.plist` (§4.2) — Q3이 "포함"일 때만
- [ ] `flutter pub get` → `dart analyze` / `dart format` 통과 (§1의 `avoid_print` 주의)

---

## 10. 완료 기준 (Acceptance Criteria)

실기기에서 확인한다. 에뮬레이터에는 카카오톡을 깔 수 없어 **앱 전환 경로를 검증하지 못한다.**

- [ ] 카카오톡이 **설치된** 기기에서 앱 전환 로그인 성공 → 자체 JWT 수신
- [ ] 카카오톡이 **없는** 기기(또는 삭제 후)에서 카카오계정 웹 로그인으로 폴백 성공
- [ ] 카카오톡 로그인 창에서 **취소**했을 때 크래시·에러 토스트 없이 웹 로그인으로 폴백
- [ ] 앱 완전 종료 후 재실행 시 저장된 JWT로 **재로그인 없이** 진입
- [ ] 재실행해도 `device_id`가 **같은 값**임을 확인 (로그 또는 디버그 화면)
- [ ] access JWT 만료(10분) 후 API 호출이 자동 갱신되고 사용자에게는 끊김이 없음
- [ ] 로그아웃 후 저장소가 비고 로그인 화면으로 이동, 이전 refresh로는 갱신 실패
- [ ] 비행기 모드에서 로그인 시 크래시 없이 네트워크 오류 안내
- [ ] **릴리스 서명 빌드**에서도 로그인 성공 (릴리스 키 해시 등록 검증 — 디버그만
      등록한 채 배포하면 여기서 처음 깨진다)
- [ ] `dart analyze` 무경고, `dart format` 차이 없음
