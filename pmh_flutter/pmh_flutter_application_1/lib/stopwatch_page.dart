import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';

import 'image_upload_page.dart';

/// iPhone 시계 앱의 스톱워치 화면을 순수 Flutter 위젯으로 재구성한다.
///
/// 경과 시간의 유일한 출처는 `dart:core`의 [Stopwatch]다. [Ticker]는 매 프레임
/// 다시 그리는 역할만 한다 — `Timer.periodic`으로 카운트를 직접 더하면 프레임
/// 지연이 누적돼 실제 시간과 어긋난다.
class StopwatchPage extends StatefulWidget {
  const StopwatchPage({super.key});

  @override
  State<StopwatchPage> createState() => _StopwatchPageState();
}

/// 애플 시계 앱의 다크 팔레트.
class _SwColors {
  static const bg = Color(0xFF000000);
  static const fg = Color(0xFFFFFFFF);
  static const divider = Color(0x1FFFFFFF);
  static const neutralButton = Color(0xFF323234);
  static const stopButton = Color(0xFF35100D);
  static const stopLabel = Color(0xFFFF453A);
  static const startButton = Color(0xFF0B2B15);
  static const startLabel = Color(0xFF30D158);
  static const disabledLabel = Color(0xFF6E6E73);
  static const shortest = Color(0xFF30D158);
  static const longest = Color(0xFFFF453A);

  /// 스톱워치 팔레트에는 없는 색이다 — 앱의 시안 포인트를 그대로 써서 이 버튼이
  /// 스톱워치 기능이 아니라 **다른 화면으로 나가는 입구**임을 구분한다.
  static const uploadEntry = Color(0xFF22D3EE);
}

/// 총 경과 시간에서 완료된 랩을 빼 **진행 중인 랩**의 시간을 구한다.
///
/// 위젯 밖 순수 함수로 두어 단위 테스트가 가능하다.
Duration currentLapElapsed(Duration total, List<Duration> completedLaps) {
  var completed = Duration.zero;
  for (final lap in completedLaps) {
    completed += lap;
  }
  return total - completed;
}

/// `mm:ss.cc` 형식. 1시간을 넘으면 `h:mm:ss.cc`.
String formatStopwatch(Duration d) {
  String two(int n) => n.toString().padLeft(2, '0');

  final hundredths = (d.inMilliseconds ~/ 10) % 100;
  final base = '${two(d.inMinutes % 60)}:${two(d.inSeconds % 60)}'
      '.${two(hundredths)}';
  return d.inHours > 0 ? '${d.inHours}:$base' : base;
}

class _StopwatchPageState extends State<StopwatchPage>
    with SingleTickerProviderStateMixin {
  final Stopwatch _stopwatch = Stopwatch();
  final List<Duration> _laps = <Duration>[];
  late final Ticker _ticker;

  @override
  void initState() {
    super.initState();
    _ticker = createTicker((_) => setState(() {}));
  }

  @override
  void dispose() {
    _ticker.dispose();
    super.dispose();
  }

  void _start() {
    _stopwatch.start();
    if (!_ticker.isActive) {
      _ticker.start();
    }
    setState(() {});
  }

  void _stop() {
    _stopwatch.stop();
    if (_ticker.isActive) {
      _ticker.stop();
    }
    setState(() {});
  }

  void _reset() {
    setState(() {
      _stopwatch.reset();
      _laps.clear();
    });
  }

  void _lap() {
    setState(() {
      _laps.add(currentLapElapsed(_stopwatch.elapsed, _laps));
    });
  }

  @override
  Widget build(BuildContext context) {
    final elapsed = _stopwatch.elapsed;
    final running = _stopwatch.isRunning;

    return Scaffold(
      backgroundColor: _SwColors.bg,
      body: SafeArea(
        child: Column(
          children: [
            // 로그인 후 도착하는 화면이라, 다른 기능으로 가는 입구를 여기 둔다.
            // 아이콘만 두면 검은 배경 모서리에 묻혀 안 보인다 — 글자를 함께 둔다.
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
              child: Align(
                alignment: Alignment.centerRight,
                child: TextButton.icon(
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute<void>(builder: (_) => const ImageUploadPage()),
                  ),
                  icon: const Icon(Icons.cloud_upload_outlined, size: 20),
                  label: const Text('이미지 업로드'),
                  style: TextButton.styleFrom(
                    foregroundColor: _SwColors.uploadEntry,
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 4),
            _TimeDisplay(elapsed: elapsed),
            const SizedBox(height: 40),
            _ControlButtons(
              running: running,
              // 정지 상태에서 0이면 초기 상태 — 좌측 버튼이 비활성이다.
              started: elapsed > Duration.zero,
              onLap: _lap,
              onReset: _reset,
              onStart: _start,
              onStop: _stop,
            ),
            const SizedBox(height: 28),
            Expanded(
              child: _LapList(
                completedLaps: _laps,
                currentLap: currentLapElapsed(elapsed, _laps),
                showCurrentLap: elapsed > Duration.zero,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TimeDisplay extends StatelessWidget {
  const _TimeDisplay({required this.elapsed});

  final Duration elapsed;

  @override
  Widget build(BuildContext context) {
    return Text(
      formatStopwatch(elapsed),
      style: const TextStyle(
        color: _SwColors.fg,
        fontSize: 78,
        fontWeight: FontWeight.w200,
        letterSpacing: -1,
        // 숫자 폭을 고정한다 — 없으면 매 프레임 너비가 바뀌어 표시가 떨린다.
        fontFeatures: [FontFeature.tabularFigures()],
      ),
    );
  }
}

class _ControlButtons extends StatelessWidget {
  const _ControlButtons({
    required this.running,
    required this.started,
    required this.onLap,
    required this.onReset,
    required this.onStart,
    required this.onStop,
  });

  final bool running;
  final bool started;
  final VoidCallback onLap;
  final VoidCallback onReset;
  final VoidCallback onStart;
  final VoidCallback onStop;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 36),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          if (running)
            _CircleButton(
              label: '랩',
              background: _SwColors.neutralButton,
              foreground: _SwColors.fg,
              onPressed: onLap,
            )
          else
            _CircleButton(
              label: started ? '재설정' : '랩',
              background: _SwColors.neutralButton,
              foreground: started ? _SwColors.fg : _SwColors.disabledLabel,
              onPressed: started ? onReset : null,
            ),
          if (running)
            _CircleButton(
              label: '중단',
              background: _SwColors.stopButton,
              foreground: _SwColors.stopLabel,
              onPressed: onStop,
            )
          else
            _CircleButton(
              label: '시작',
              background: _SwColors.startButton,
              foreground: _SwColors.startLabel,
              onPressed: onStart,
            ),
        ],
      ),
    );
  }
}

class _CircleButton extends StatelessWidget {
  const _CircleButton({
    required this.label,
    required this.background,
    required this.foreground,
    required this.onPressed,
  });

  final String label;
  final Color background;
  final Color foreground;
  final VoidCallback? onPressed;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 80,
      height: 80,
      child: TextButton(
        onPressed: onPressed,
        style: TextButton.styleFrom(
          backgroundColor: background,
          shape: const CircleBorder(),
          padding: EdgeInsets.zero,
        ),
        child: Text(
          label,
          style: TextStyle(
            color: foreground,
            fontSize: 17,
            fontWeight: FontWeight.w400,
          ),
        ),
      ),
    );
  }
}

class _LapList extends StatelessWidget {
  const _LapList({
    required this.completedLaps,
    required this.currentLap,
    required this.showCurrentLap,
  });

  final List<Duration> completedLaps;
  final Duration currentLap;
  final bool showCurrentLap;

  /// 최단·최장은 **완료된 랩끼리만** 비교한다. 진행 중인 랩은 아직 확정되지
  /// 않았고, 완료 랩이 2개 미만이면 구분할 의미가 없어 색을 넣지 않는다.
  Color? _colorFor(Duration lap) {
    if (completedLaps.length < 2) return null;

    var shortest = completedLaps.first;
    var longest = completedLaps.first;
    for (final other in completedLaps) {
      if (other < shortest) shortest = other;
      if (other > longest) longest = other;
    }
    if (lap == shortest) return _SwColors.shortest;
    if (lap == longest) return _SwColors.longest;
    return null;
  }

  @override
  Widget build(BuildContext context) {
    final rowCount = completedLaps.length + (showCurrentLap ? 1 : 0);

    return ListView.separated(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      itemCount: rowCount,
      separatorBuilder: (_, _) => const Divider(
        height: 1,
        thickness: 1,
        color: _SwColors.divider,
      ),
      itemBuilder: (context, index) {
        // 맨 위가 진행 중인 랩, 그 아래로 완료된 랩이 역순이다.
        if (showCurrentLap && index == 0) {
          return _LapRow(
            number: completedLaps.length + 1,
            time: currentLap,
            color: null,
          );
        }
        final lapIndex =
            completedLaps.length - 1 - (showCurrentLap ? index - 1 : index);
        final lap = completedLaps[lapIndex];
        return _LapRow(
          number: lapIndex + 1,
          time: lap,
          color: _colorFor(lap),
        );
      },
    );
  }
}

class _LapRow extends StatelessWidget {
  const _LapRow({
    required this.number,
    required this.time,
    required this.color,
  });

  final int number;
  final Duration time;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    final style = TextStyle(
      color: color ?? _SwColors.fg,
      fontSize: 17,
      fontFeatures: const [FontFeature.tabularFigures()],
    );

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 14),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text('랩 $number', style: style),
          Text(formatStopwatch(time), style: style),
        ],
      ),
    );
  }
}
