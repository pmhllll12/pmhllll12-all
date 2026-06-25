# 플러터 (`pmh_flutter`) — LLM 코딩 지침

Flutter 앱. 진입점은 [`pmh_flutter_application_1/lib/main.dart`](pmh_flutter_application_1/lib/main.dart) — `www`의 다크 테마·시안 포인트 컬러를 순수 위젯으로 재구성한다.

공통 4원칙 전문 ---> [`../_docs/CLAUDE.md`](../_docs/CLAUDE.md)
모노레포 지도 ---> [`../CLAUDE.md`](../CLAUDE.md)

---

## 실행

```powershell
cd pmh_flutter/pmh_flutter_application_1
flutter pub get
flutter run
```

---

## Lint / Format

`analysis_options.yaml`(`flutter_lints` + `avoid_print` 등 추가 규칙)이 `dart analyze` /
`dart format`, PR마다 루트 `.github/workflows/flutter-lint.yml`로 강제된다.
상세 ---> [`_docs/linting.md`](_docs/linting.md)
