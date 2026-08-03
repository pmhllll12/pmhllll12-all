# 안드로이드 실제 기기 개발 하네스

`pmh_flutter_application_1`을 **안드로이드 실기기**에 올려 돌리기 위한 절차.
USB(데이터 케이블로 폰 ↔ 개발 PC 연결)와 Wi-Fi 무선 디버깅 두 가지를 다룬다.

에뮬레이터가 아니라 실기기를 쓰는 이유는 터치·스크롤 관성, 다크 테마 대비, 실제
GPU에서의 렌더링 성능처럼 에뮬레이터가 재현하지 못하는 부분을 검증하기 위해서다.

린트/포맷 하네스 ---> [`linting.md`](linting.md)
플러터 영역 지침 ---> [`../CLAUDE.md`](../CLAUDE.md)

---

## 0. 기준 버전 (2026-07 확인)

이 저장소가 실제로 쓰는 값이다. 문서와 코드가 어긋나면 **코드가 정본**이다.

| 항목 | 값 | 출처 |
|------|----|------|
| Flutter / Dart | 3.44.x / Dart 3.12 (`pubspec.yaml` `sdk: ^3.12.2`) | [`pubspec.yaml`](../pmh_flutter_application_1/pubspec.yaml) |
| Android Gradle Plugin | 9.0.1 | [`android/settings.gradle.kts`](../pmh_flutter_application_1/android/settings.gradle.kts) |
| Gradle | 9.1.0 | `android/gradle/wrapper/gradle-wrapper.properties` |
| Kotlin | 2.3.20 | `android/settings.gradle.kts` |
| Java 소스/타깃 | 17 (`JvmTarget.JVM_17`) | [`android/app/build.gradle.kts`](../pmh_flutter_application_1/android/app/build.gradle.kts) |
| compileSdk / minSdk / targetSdk | `flutter.*` 위임 → Flutter 3.44 기준 compile 36 · min 24 | `android/app/build.gradle.kts` |
| Android Studio | 최신 안정판(2026-07-31 기준 **Quail 3**, 07/30 릴리스) | 아래 참고 링크 |

Flutter 3.44가 지원하는 Android API는 **24(7.0) ~ 37(Android 17)**, CI 검증 범위는 24~36이다.
API 23 이하는 지원하지 않는다. 즉 실기기는 **Android 7.0 이상**이어야 한다.

> 책·블로그에 흔한 "minSdk 21 / API 16 이상이면 USB 디버깅 가능" 같은 문장은 낡았다.
> `minSdk`를 직접 박지 말고 위처럼 `flutter.minSdkVersion` 위임을 유지한다.

---

## 1. 공통: 개발자 옵션 · USB 디버깅 켜기

USB든 무선이든 먼저 해야 하는 공통 작업이다. Android 11(API 30) 이후로는 경로가
사실상 하나로 정리됐다. 버전별로 갈라지던 옛 절차는 필요 없다.

1. **빌드번호 7번 탭** — 순정(Pixel·AOSP): `설정 → 휴대전화 정보 → 빌드번호`.
   삼성 One UI: `설정 → 휴대전화 정보 → 소프트웨어 정보 → 빌드번호`.
   샤오미(HyperOS): `설정 → 내 기기 → 전체 사양 → MIUI/HyperOS 버전`.
   "개발자가 되었습니다" 토스트가 뜨면 성공. 화면 잠금이 걸려 있으면 PIN을 묻는다.
2. **개발자 옵션 진입** — `설정 → 시스템 → 개발자 옵션`
   (삼성은 `설정` 최하단에 `개발자 옵션`이 바로 노출된다).
3. **USB 디버깅** 켜기. 무선으로 붙일 거라면 같은 화면의 **무선 디버깅**도 켠다.

제조사 UI마다 위치만 다를 뿐 `USB 디버깅` / `무선 디버깅` 항목 이름은 동일하다.

---

## 2. 개발 PC 준비 (한 번만)

Android Studio 최신 안정판을 설치한 뒤 SDK Manager에서 컴포넌트를 맞춘다.

1. `Tools → SDK Manager` (환영 화면이면 `More Actions → SDK Manager`).
2. **SDK Platforms** 탭 — **API 36 (Android 16)** 설치/업데이트.
3. **SDK Tools** 탭 — 아래를 설치한다.
   - Android SDK Build-Tools
   - Android SDK Command-line Tools ← `sdkmanager` 등 CLI 도구
   - Android SDK Platform-Tools ← **`adb` 본체. 무선 디버깅에 필수**
   - Android Emulator, CMake, NDK (Side by side)
4. **Windows에서 USB로 붙일 때만** 드라이버가 필요하다.
   Pixel/Nexus 계열은 SDK Tools 탭의 **Google USB Driver**를 체크해 설치하고,
   그 외 제조사(삼성·샤오미 등)는 제조사가 배포하는 OEM USB 드라이버를 설치한다.
   **macOS·Linux는 드라이버 설치가 필요 없다.** Linux는 대신 udev 규칙이 없으면
   기기가 `no permissions`로 잡히므로 `android-udev-rules` 설정이 필요할 수 있다.
5. 라이선스 동의 — 개발 PC 셸에서:

```powershell
flutter doctor --android-licenses   # 전부 y. 끝에 "All SDK package licenses accepted."
flutter doctor -v                   # Android toolchain 항목에 체크가 떠야 한다
```

`flutter doctor -v`의 `Java binary at:` 경로가 Android Studio 번들 JDK를 가리키는지
확인한다. Flutter는 별도 설정이 없으면 이 JDK로 Gradle을 돌린다. 예전에 설치한
JDK 8·11이 `JAVA_HOME`을 잡고 있으면 AGP 9 빌드가 깨진다(빌드 JDK 17 이상 필요).

---

## 3. USB로 연결하기

1. 데이터 케이블로 폰과 개발 PC를 연결한다. **충전 전용 케이블은 인식되지 않는다** —
   기기가 안 잡히면 케이블부터 바꿔본다.
2. 폰에 뜨는 **"USB 디버깅을 허용하시겠습니까?"** 대화상자에서
   *이 컴퓨터에서 항상 허용*을 체크하고 허용한다.
3. USB 연결 모드를 *파일 전송(MTP)* 으로 두면 인식률이 좋다(충전 전용 모드에서 실패하는 기기가 있다).
4. 개발 PC에서 확인:

```powershell
adb devices     # <serial>  device  로 떠야 한다
flutter devices # 플랫폼이 android 로 표시돼야 한다
```

`unauthorized`로 뜨면 2번 대화상자를 놓친 것이다. 케이블을 다시 꽂거나
`개발자 옵션 → USB 디버깅 승인 취소` 후 재연결한다.

---

## 4. Wi-Fi 무선 디버깅으로 연결하기

**Android 11(API 30) 이상**이면 케이블 없이 처음부터 무선으로 붙을 수 있다.
폰과 개발 PC가 **같은 네트워크**에 있어야 한다(게스트 Wi-Fi·AP 격리 모드면 실패).

1. 폰: `개발자 옵션 → 무선 디버깅` ON → **페어링 코드로 기기 페어링**.
   → IP·**페어링 포트**·6자리 코드가 뜬다.
2. 개발 PC:

```powershell
adb pair 192.168.0.10:37251     # 페어링 포트. 실행 후 6자리 코드 입력
adb connect 192.168.0.10:41235  # 무선 디버깅 화면 상단의 접속 포트 — 페어링 포트와 다르다
adb devices
```

**포트가 두 개**라는 점이 가장 많이 틀리는 지점이다. `adb pair`에 쓰는 포트와
`adb connect`에 쓰는 포트는 서로 다르고, 페어링 포트는 매번 바뀐다.

페어링은 **한 번만** 하면 된다. 이후에는 같은 네트워크에서 `adb connect`만 하면 되고,
Android Studio를 쓴다면 `Pair devices over Wi-Fi` 대화상자에서 QR 코드로 페어링해도 된다.

Android 10 이하 기기라면 무선 페어링이 없으므로 USB로 한 번 붙인 뒤 전환한다:

```powershell
adb tcpip 5555                    # USB 연결 상태에서 실행
adb connect 192.168.0.10:5555     # 케이블 뽑고 연결
```

---

## 5. 앱 실행

```powershell
cd pmh_flutter/pmh_flutter_application_1
flutter pub get
flutter devices                   # 대상 기기 ID 확인
flutter run -d <device-id>        # 실기기에 설치·실행
```

실행 중 셸에서 `r`(hot reload) / `R`(hot restart) / `q`(종료).
첫 빌드는 Gradle 의존성을 받느라 수 분 걸린다. 렌더러는 Impeller가 기본이며,
실기기에서만 재현되는 렌더링 이슈는 `flutter run --enable-impeller=false`로
Impeller 원인 여부를 가려낼 수 있다.

---

## 6. 검증 체크리스트

"됐다" 대신 아래가 전부 통과해야 연동 완료로 본다.

- [ ] `flutter doctor -v` — Android toolchain 체크, 라이선스 전부 수락됨
- [ ] `adb devices` — 대상 기기가 `device` 상태(`unauthorized`·`offline` 아님)
- [ ] `flutter devices` — 해당 기기가 플랫폼 `android`로 표시됨
- [ ] `flutter run -d <device-id>` — 기기 화면에 앱이 뜸
- [ ] 코드 한 줄 수정 후 `r` — hot reload가 기기에 반영됨

---

## 7. 트러블슈팅

| 증상 | 원인 / 조치 |
|------|-------------|
| `adb devices`에 아무것도 없음 | 충전 전용 케이블 / Windows 드라이버 미설치 / USB 디버깅 꺼짐 |
| `unauthorized` | 폰의 디버깅 허용 대화상자 미승인. `USB 디버깅 승인 취소` 후 재연결 |
| `offline` (무선) | `adb kill-server` 후 `adb connect <ip>:<port>` 재시도 |
| 재부팅 후 무선 연결 끊김 | 정상. 접속 포트가 바뀌므로 `adb connect`를 다시 한다(페어링은 유지) |
| `adb pair` 타임아웃 | 페어링 포트 오타 / 다른 서브넷 / 공유기 AP 격리(클라이언트 간 통신 차단) |
| Gradle 빌드 실패, JDK 관련 오류 | `JAVA_HOME`이 낡은 JDK를 가리킴. AGP 9는 빌드 JDK 17 이상 필요 |
| `Installed Build Tools revision ... is corrupted` | SDK Manager에서 Build-Tools 재설치 |
| 앱이 설치는 되는데 바로 꺼짐 | `flutter logs` / `adb logcat`으로 네이티브 예외 확인 |

---

## 참고

- [Set up Android development (Flutter 공식)](https://docs.flutter.dev/platform-integration/android/setup)
- [Flutter 지원 플랫폼 · API 레벨](https://docs.flutter.dev/reference/supported-platforms)
- [Android Debug Bridge (adb) — 무선 디버깅](https://developer.android.com/tools/adb)
- [기기별 개발자 옵션 설정](https://developer.android.com/studio/debug/dev-options)
- [OEM USB 드라이버 (Windows)](https://developer.android.com/studio/run/oem-usb)
- [Android Studio 릴리스 노트](https://androidstudio.googleblog.com/)

### 원문(교재 5.3.1) 대비 갱신한 부분

| 교재 서술 | 현재 |
|-----------|------|
| API 25/26/28별로 갈라지는 개발자 옵션 경로 | Android 11+ 단일 경로. 제조사 UI 차이만 남음 |
| "Android 4.1(API 16) 이상이면 USB 디버깅 가능" | Flutter 3.44 지원 하한은 **API 24(Android 7.0)** |
| `SDK Manager → Google USB Driver` 필수 | **Windows·Pixel 계열 한정.** 타 제조사는 OEM 드라이버, macOS/Linux는 불필요 |
| 무선 디버깅은 "참고 링크" 수준 | Android 11+ 표준 기능. `adb pair` → `adb connect` 절차를 본문에 포함 |
| 설치 문서 링크가 `get-started/install/windows` | 해당 URL은 폐기(404). 현재는 `platform-integration/android/setup` |
