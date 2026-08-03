---
name: flutter-note9-impeller
description: 갤럭시 노트9에서 video_player 영상이 Impeller 렌더러로는 검게만 나온다 — --no-enable-impeller 로 확인됨
metadata: 
  node_type: memory
  type: project
  originSessionId: 1f5d183a-f1b9-4e06-9b05-4b1a88daf23a
  modified: 2026-07-31T08:19:37.808Z
---

`pmh_flutter_application_1` 을 갤럭시 노트9(SM-N960N, Android 10, Mali GPU)에서 돌리면
`video_player` 의 영상이 **디코딩은 되는데 화면에 안 그려진다**. 2026-07-31에 확인했다.

로그상 정상 신호가 다 나온다 — `OMX.Exynos.avc.dec` 가 1280×720 표면에 연결되고,
`[intro] 초기화 완료`, 4초 뒤 `ExoPlayerImpl: Release`. 그런데 화면은 검다.
단서는 두 줄이다:

    Using the Impeller rendering backend (OpenGLES)
    ImageReaderSurfaceProducer: ImageTextureEntry can't wait on the fence on Android < 33

`flutter run --no-enable-impeller` 로 실행하면 영상이 정상적으로 보인다.

**Why:** 로그에 오류가 없어 코드·코덱·에셋 쪽을 계속 파게 되는데, 원인은 렌더러다.
디코딩 성공과 화면 표시는 별개라는 점을 로그만으로는 구분할 수 없다.

**How to apply:**
- 플래그 표기는 `--no-enable-impeller` 다. `--enable-impeller=false` 는 Flutter 3.44에서
  `Flag option "--enable-impeller" should not be given a value.` 로 거부된다.
  `pmh_flutter/_docs/flutter-android-harness.md` 143번째 줄이 틀린 표기로 적혀 있다 — 고쳐야 한다.
- 매번 플래그를 붙이지 않으려면 `AndroidManifest.xml` 에 Impeller 비활성 메타데이터를 넣는다(미적용).
- 구형 안드로이드 기기에서 "영상만 검다"면 코드보다 렌더러를 먼저 의심한다.

관련: [[wsl-local-clone-workflow]]
