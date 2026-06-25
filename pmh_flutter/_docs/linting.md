# Lint / Format 하네스

`pmh_flutter_application_1/analysis_options.yaml`은 `flutter_lints` 기본값만 쓰고
있었다. 명시적으로 강제하는 규칙을 추가했다.

## 설정

[`analysis_options.yaml`](../pmh_flutter_application_1/analysis_options.yaml):

- `avoid_print`, `prefer_const_constructors`, `avoid_unnecessary_containers`,
  `use_super_parameters` 린트 활성화.
- `avoid_print`는 `analyzer.errors`에서 `error`로 강제 — 경고로 두면 무시되기 쉽다.

## 실행

```powershell
cd pmh_flutter/pmh_flutter_application_1
flutter pub get
dart analyze .
dart format --output=none --set-exit-if-changed .   # 변경 없이 체크만
dart format .                                         # 실제 포맷 적용
```

도입 시점 기준 `main.dart`에 `prefer_const_constructors` info 3건이 남아 있다
(차단되는 수준은 아님 — `error`로 지정한 `avoid_print`만 종료 코드를 0이 아니게 만든다).

## CI

`pmh_flutter`는 서브모듈이 아니라 이 저장소(`cloud.pmhllll12`)의 일반 디렉터리라
루트 `.github/workflows/flutter-lint.yml`이 `pmh_flutter/**` 변경에 반응한다.
