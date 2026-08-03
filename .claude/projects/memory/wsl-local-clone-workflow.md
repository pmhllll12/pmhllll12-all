---
name: wsl-local-clone-workflow
description: 코드는 EC2에서 편집하지만 실행·검증은 사용자의 로컬 WSL 클론에서 한다 — 푸시 후 git checkout 으로 넘겨야 반영된다
metadata: 
  node_type: memory
  type: project
  originSessionId: 1f5d183a-f1b9-4e06-9b05-4b1a88daf23a
  modified: 2026-07-31T08:19:49.834Z
---

저장소 체크아웃이 **두 개**다. 내가 편집하는 곳은 EC2의 `/home/ec2-user/pmhllll12-all`,
사용자가 `flutter run` 등을 돌리는 곳은 로컬 WSL(`hi@DESKTOP-J5H10MP`)의
`~/projects/pmhllll12-all` 이다. EC2에는 Flutter/Dart SDK가 없어 `flutter analyze`·`test`·`run`
을 내가 직접 돌릴 수 없다.

**Why:** 이 구분을 놓치면 "고쳤는데 왜 그대로냐"가 반복된다. 2026-07-31 세션에서 사용자가
받아오지 않은 채 실행해 예전 화면을 보고 버그로 오인한 일이 세 번 있었다.

**How to apply:**
- 편집 → 커밋 → 푸시 → 사용자가 로컬에서 받아야 비로소 검증된다. 브랜치 전환 없이 파일만
  가져오는 형태가 로컬 작업물을 안 건드려 안전하다:

      git checkout origin/<브랜치> -- pmh_flutter/pmh_flutter_application_1/lib

  로컬 브랜치가 없으면 `origin/` 접두사가 필수다. `git checkout <브랜치> -- <경로>` 는
  `fatal: invalid reference` 로 실패한다(경로 지정 형태에서는 브랜치 이름 자동 해석이 없다).
- 증상 보고를 받으면 **로컬에 새 코드가 실제로 있는지부터** 확인한다(`grep`/`ls`).
- 검증하지 않은 것은 검증하지 않았다고 말한다. 내가 돌릴 수 있는 명령이 없다.

관련: [[ssh-remote-session]], [[flutter-note9-impeller]]
