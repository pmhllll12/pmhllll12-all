import 'dart:async';

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

import 'chat_page.dart';

/// 영상이 **재생되기 시작한 시점부터** 인트로를 보여주는 시간.
const _introDuration = Duration(seconds: 4);

/// 영상 준비를 기다리는 한계 시간. 이 안에 재생이 시작되지 않으면 영상을
/// 포기하고 넘어간다 — 파일이 깨졌거나 디코더가 없어도 앱이 멈추지 않게 한다.
const _readyTimeout = Duration(seconds: 10);

/// 앱 시작 화면. `assets/video/intro.mp4` 를 재생하고, 재생 시작 4초 뒤
/// [ChatPage] 로 넘어간다.
class IntroVideoPage extends StatefulWidget {
  const IntroVideoPage({super.key});

  @override
  State<IntroVideoPage> createState() => _IntroVideoPageState();
}

class _IntroVideoPageState extends State<IntroVideoPage> {
  late final VideoPlayerController _controller;
  Timer? _timer;

  @override
  void initState() {
    super.initState();

    _controller = VideoPlayerController.asset('assets/video/intro.mp4');
    _controller
        .initialize()
        .then((_) {
          debugPrint(
            '[intro] 초기화 완료 size=${_controller.value.size} '
            'duration=${_controller.value.duration}',
          );
          if (!mounted) return;
          // 브라우저는 소리가 있는 영상의 자동 재생을 막는다 — 음소거해야
          // 웹에서도 사용자 조작 없이 재생된다.
          _controller.setVolume(0);
          _controller.play();
          setState(() {});

          // 4초는 여기서부터 센다. initState에서 세기 시작하면 디버그 빌드의
          // 시작 지연(프레임 스킵 수 초)만으로 인트로가 끝나 버린다.
          _timer?.cancel();
          _timer = Timer(_introDuration, _goToChat);
        })
        .catchError((Object error) {
          // 넘어가는 것은 아래 대기 한계 타이머가 책임지므로 화면은 검은
          // 상태로 두되, 원인은 로그로 남긴다.
          debugPrint('[intro] 초기화 실패: $error');
        });

    // 재생이 시작되지 않는 경우의 안전장치. 재생이 시작되면 위에서 교체된다.
    _timer = Timer(_readyTimeout, _goToChat);
  }

  void _goToChat() {
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(builder: (_) => const ChatPage()),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: _controller.value.isInitialized
          ? SizedBox.expand(
              // 화면비가 달라도 여백 없이 꽉 채운다.
              child: FittedBox(
                fit: BoxFit.cover,
                child: SizedBox(
                  width: _controller.value.size.width,
                  height: _controller.value.size.height,
                  child: VideoPlayer(_controller),
                ),
              ),
            )
          : const SizedBox.shrink(),
    );
  }
}
