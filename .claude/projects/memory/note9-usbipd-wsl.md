---
name: note9-usbipd-wsl
description: "갤럭시 노트9를 WSL에 붙일 때 usbipd가 계속 끊긴다 — detach 후 단일 attach가 답이고, 붙으면 adb tcpip로 갈아탄다"
metadata: 
  node_type: memory
  type: project
  originSessionId: 582def62-cd0b-48f3-883b-e87b696ba9f0
  modified: 2026-08-03T04:10:03.087Z
---

WSL(`DESKTOP-J5H10MP`)에서 갤럭시 노트9(SM-N960N, Android 10)에 `flutter run` 하려면
윈도우의 USB를 usbipd-win으로 넘겨야 하는데, 이 구간이 매우 불안정하다. 2026-08-03에 겪었다.

**무선 디버깅(`adb pair`)은 Android 11부터라 노트9엔 메뉴 자체가 없다.** 폰에서 찾지 말 것.

## 실제로 통한 순서

    usbipd list                         # 노트9 BUSID 확인 (STATE: Shared)
    usbipd detach --busid 1-6           # ★ 이 줄이 핵심
    usbipd attach --wsl --busid 1-6     # --auto-attach 없이 단일 실행

`--auto-attach` 루프는 오히려 해로웠다 — 8초 간격으로 attach/detach를 반복하며
`Failed to attach`를 섞어 내고, 그러다 장치가 윈도우 `Connected` 목록에서 통째로
사라져 `Persisted`로 내려갔다. 그 상태에선 `usbipd attach`가
`There is no device with busid '1-6'` 를 낸다 → 케이블을 뽑았다 다시 꽂아야 돌아온다.

`Device with busid '1-6' is already attached to a client.` 가 뜨는데 WSL의 `lsusb`엔
안 보이면 상태가 어긋난 것이다. **`detach` 후 다시 `attach` 하면 붙는다.**

## 헷갈리지 말 것

- `lsusb`의 `(MTP mode)` 표기는 **USB 디버깅 on/off와 무관하다.** `04e8:6860` VID:PID에
  대한 usb.ids의 고정 설명일 뿐이라, 디버깅이 켜져 정상 연결된 상태에서도 똑같이
  `(MTP mode)` 로만 나온다. 이걸 보고 "ADB 인터페이스가 없다"고 판단하면 엉뚱한 데를 판다.
  판단은 `adb devices` 로만 한다.
- 명령은 `usbipd` 다. `usbipd-win` 은 제품명이라 셸에서 인식되지 않는다.
- 윈도우 PowerShell에는 `adb` 가 없다(platform-tools 미설치). adb는 WSL 쪽에 있다.

## 붙고 나면 무선으로 갈아탄다

케이블을 다시 꽂는 일을 없애려면, 연결된 김에 tcpip 모드로 바꿔 둔다.
노트9는 Android 11 미만이라 이 구형 방식이 된다.

    adb tcpip 5555
    adb shell ip -f inet addr show wlan0   # 폰 IP
    # 케이블 분리 후
    adb connect <폰IP>:5555

폰을 재부팅하면 tcpip 모드가 풀리므로 그때만 케이블을 한 번 꽂는다.

**Why:** usbipd 구간만 불안정하고 윈도우–폰 USB 자체는 멀쩡하다. 무선으로 넘기면
그 구간을 아예 쓰지 않는다.

**How to apply:** 폰 연결이 안 될 때 `usbipd detach` → `attach` 를 먼저 시도하고,
성공하는 즉시 `adb tcpip 5555` 로 무선 전환한다. 실행은 항상
`flutter run --no-enable-impeller` — 이유는 [[flutter-note9-impeller]].

관련: [[wsl-local-clone-workflow]]
