---
name: ssh-remote-session
description: "이 세션은 로컬 PC에서 EC2로 SSH 접속한 원격 터미널 — 클립보드/이미지 붙여넣기 불가, macOS 명령도 없음"
metadata: 
  node_type: memory
  type: project
  originSessionId: ed4a617e-5cea-4a65-b6b6-de85bd43bffa
  modified: 2026-08-03T06:16:13.940Z
---

Claude Code CLI는 **EC2 리눅스**(Amazon Linux, `/home/ec2-user/pmhllll12-all`)에서 실행되고, 사용자는 로컬 PC에서 SSH로 접속한다. `DISPLAY` 없음, `xclip`/`xsel`/`wl-paste`/`pbpaste` 전부 없음, `osascript` 없음.

**Why:** CLI가 도는 머신 기준으로 클립보드·OS 명령이 결정되므로, 로컬 PC의 클립보드나 macOS 도구를 전제한 해법은 여기서 전부 실패한다. 2026-07-30에 `.claude/settings.json`의 Notification 훅이 `osascript`를 호출해 매번 실패하던 것을 크로스 플랫폼 폴백(`osascript || notify-send || printf '\a'`)으로 고쳤다.

**How to apply:**
- 이미지 첨부 요청 시 붙여넣기/드래그앤드롭을 안내하지 말 것. **사용자가 이미 쓰는 방식은 저장소 루트의 `tmp.png` 를 덮어쓰고 `@tmp.png` 로 참조하는 것이다** — 2026-08-03 확인. 윈도우키+PrintScreen으로 캡처해 파일명을 `tmp.png` 로 고정한다. "tmp.png 로 덮어써 주세요"라고 안내하면 된다. `scp`로 `/home/ec2-user/inbox`(이미 `permissions.additionalDirectories`에 등록됨)에 올리는 것은 대안이며, 사용자에게 더 번거롭다. 또 다른 대안은 `claude remote-control` + claude.ai/code 브라우저 첨부.
- `c:/Users/...` 같은 로컬 경로를 주시면 EC2에서 열 수 없다고 말하고 위 방식을 안내한다.
- 훅·스크립트를 쓸 때 macOS 전용 명령(`osascript`, `pbcopy`, `open`)을 기본으로 쓰지 말 것. 사용자가 맥도 병행할 수 있으니 폴백 체인으로 작성한다.
