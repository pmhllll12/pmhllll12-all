import 'dart:async';

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

import 'stopwatch_page.dart';

/// 인트로 영상을 보여주는 시간. 영상 길이와 무관하게 이 시간이 지나면 넘어간다.
const _introDuration = Duration(seconds: 4);

/// 앱 시작 화면. `assets/video/intro.mp4` 를 재생하다가 4초 뒤
/// [StopwatchPage] 로 넘어간다.
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
          if (!mounted) return;
          // 브라우저는 소리가 있는 영상의 자동 재생을 막는다 — 음소거해야
          // 웹에서도 사용자 조작 없이 재생된다.
          _controller.setVolume(0);
          _controller.play();
          setState(() {});
          debugPrint(
            '[intro] 초기화 완료 size=${_controller.value.size} '
            'duration=${_controller.value.duration}',
          );
        })
        .catchError((Object error) {
          // 넘어가는 것은 타이머가 책임지므로 화면은 검은 상태로 두되,
          // 원인은 로그로 남긴다.
          debugPrint('[intro] 초기화 실패: $error');
        });

    // 영상 로딩·재생의 성공 여부와 무관하게 4초 뒤 넘어간다. 영상이 없거나
    // 코덱을 못 읽어도 앱이 인트로에서 멈추지 않게 하기 위함이다.
    _timer = Timer(_introDuration, _goToStopwatch);
  }

  void _goToStopwatch() {
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(builder: (_) => const StopwatchPage()),
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
