import 'dart:async';

import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';

import 'auth.dart';

/// 영상 준비를 기다리는 한계 시간. 이 안에 재생이 시작되지 않으면 영상을
/// 포기하고 넘어간다 — 파일이 깨졌거나 디코더가 없어도 앱이 멈추지 않게 한다.
const _readyTimeout = Duration(seconds: 10);

/// 재생 완료 신호를 놓쳤을 때를 대비해 영상 길이에 더해 두는 여유.
///
/// 완료 판정은 `position >= duration` 인데, 플랫폼에 따라 마지막 프레임에서
/// position이 duration에 몇 ms 못 미친 채 멈추는 경우가 있다. 그러면 리스너가
/// 영영 발화하지 않아 인트로에 갇힌다.
const _endSlack = Duration(seconds: 2);

/// 앱 시작 화면. `assets/video/intro.mp4` 를 **끝까지** 재생한 뒤 [AuthPage] 로
/// 넘어간다.
///
/// 고정 시간(4초)이 아니라 재생 완료를 감지하는 이유는 영상을 교체했을 때
/// 상수를 같이 고치지 않으면 끝나기 전에 잘리거나 검은 화면이 남기 때문이다.
///
/// 이미 로그인한 기기는 `main()` 이 이 화면을 건너뛰므로 여기까지 오지 않는다.
class IntroVideoPage extends StatefulWidget {
  const IntroVideoPage({super.key});

  @override
  State<IntroVideoPage> createState() => _IntroVideoPageState();
}

class _IntroVideoPageState extends State<IntroVideoPage> {
  late final VideoPlayerController _controller;
  Timer? _timer;

  /// 완료 리스너와 안전장치 타이머가 동시에 발화할 수 있다. 화면 전환은 한 번만.
  bool _leaving = false;

  @override
  void initState() {
    super.initState();

    _controller = VideoPlayerController.asset('assets/video/intro.mp4');
    _controller
        .initialize()
        .then((_) {
          final duration = _controller.value.duration;
          debugPrint(
            '[intro] 초기화 완료 size=${_controller.value.size} duration=$duration',
          );
          if (!mounted) return;
          // 브라우저는 소리가 있는 영상의 자동 재생을 막는다 — 음소거해야
          // 웹에서도 사용자 조작 없이 재생된다.
          _controller.setVolume(0);
          _controller.play();
          setState(() {});

          _controller.addListener(_onPlaybackTick);

          // 안전장치는 여기서부터 센다. initState에서 세기 시작하면 디버그 빌드의
          // 시작 지연(프레임 스킵 수 초)만으로 인트로가 끝나 버린다.
          _timer?.cancel();
          _timer = Timer(duration + _endSlack, _goToAuth);
        })
        .catchError((Object error) {
          // 넘어가는 것은 아래 대기 한계 타이머가 책임지므로 화면은 검은
          // 상태로 두되, 원인은 로그로 남긴다.
          debugPrint('[intro] 초기화 실패: $error');
        });

    // 재생이 시작되지 않는 경우의 안전장치. 재생이 시작되면 위에서 교체된다.
    _timer = Timer(_readyTimeout, _goToAuth);
  }

  /// 매 프레임 호출된다 — 재생이 끝까지 갔으면 로그인 화면으로 넘어간다.
  void _onPlaybackTick() {
    final value = _controller.value;
    if (!value.isInitialized || value.duration == Duration.zero) return;
    if (value.position >= value.duration) {
      _goToAuth();
    }
  }

  void _goToAuth() {
    if (_leaving || !mounted) return;
    _leaving = true;
    _controller.removeListener(_onPlaybackTick);
    Navigator.of(context).pushReplacement(
      MaterialPageRoute<void>(builder: (_) => const AuthPage()),
    );
  }

  @override
  void dispose() {
    _timer?.cancel();
    _controller.removeListener(_onPlaybackTick);
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
