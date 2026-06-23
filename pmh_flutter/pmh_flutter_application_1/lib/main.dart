import 'package:flutter/material.dart';

/// 웹(`www/src/app/(site)/page.tsx`, `Hero.tsx`)의 다크 테마·시안 포인트 컬러를
/// 그대로 옮긴 디자인 토큰. 웹뷰가 아닌 순수 Flutter 위젯으로 재구성한다.
class AppColors {
  static const bg0 = Color(0xFF04070F);
  static const bg1 = Color(0xFF0A1020);
  static const fg0 = Color(0xFFFFFFFF);
  static const fg1 = Color(0xFFCBD5E1);
  static const fg2 = Color(0xFF94A3B8);
  static const fg3 = Color(0xFF64748B);
  static const accent = Color(0xFF22D3EE);
  static const accentStrong = Color(0xFF06B6D4);
  static const accentSoft = Color(0x2E22D3EE); // rgba(34,211,238,.18)
  static const border = Color(0x2E94A3B8); // rgba(148,163,184,.18)
  static const chipBg = Color(0x14949CB8); // rgba(148,163,184,.08)
  static const chipBorder = Color(0x38949CB8); // rgba(148,163,184,.22)
}

void main() {
  runApp(const WorldCupApp());
}

class WorldCupApp extends StatelessWidget {
  const WorldCupApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WORLDCUP',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        scaffoldBackgroundColor: AppColors.bg0,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.accent,
          brightness: Brightness.dark,
          primary: AppColors.accent,
          surface: AppColors.bg1,
        ),
      ),
      home: const IntroScreen(),
    );
  }
}

class IntroScreen extends StatelessWidget {
  const IntroScreen({super.key});

  void _showComingSoon(BuildContext context, String label) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('$label · 준비 중입니다'),
        backgroundColor: AppColors.bg1,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.bg0,
      body: Stack(
        children: [
          const _BackgroundGlow(),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(20, 16, 20, 40),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 720),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const _BrandBar(),
                      const SizedBox(height: 40),
                      const _SchedulePill(),
                      const SizedBox(height: 20),
                      const _HeroTitle(),
                      const SizedBox(height: 20),
                      Text(
                        '조별 리그부터 결승까지 — 일정·대진·골 순위·하이라이트를 한 곳에 모아\n'
                        '월드컵의 모든 순간을 함께 안내하는 시스템입니다.',
                        style: TextStyle(
                          color: AppColors.fg2,
                          fontSize: 16,
                          height: 1.7,
                        ),
                      ),
                      const SizedBox(height: 28),
                      _ActionButtons(onTap: _showComingSoon),
                      const SizedBox(height: 28),
                      const _ChipList(),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// CSS의 radial-gradient 글로우(.home__bg)를 흐린 원형 블롭으로 재현.
class _BackgroundGlow extends StatelessWidget {
  const _BackgroundGlow();

  @override
  Widget build(BuildContext context) {
    return Positioned.fill(
      child: DecoratedBox(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [AppColors.bg1, AppColors.bg0],
          ),
        ),
        child: Stack(
          children: [
            Positioned(
              top: -80,
              left: -60,
              child: _glowBlob(const Color(0x3822D3EE), 320),
            ),
            Positioned(
              bottom: -60,
              right: -80,
              child: _glowBlob(const Color(0x2438BDF8), 300),
            ),
          ],
        ),
      ),
    );
  }

  Widget _glowBlob(Color color, double size) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        gradient: RadialGradient(colors: [color, color.withAlpha(0)]),
      ),
    );
  }
}

class _BrandBar extends StatelessWidget {
  const _BrandBar();

  @override
  Widget build(BuildContext context) {
    return const Text(
      'WORLDCUP',
      style: TextStyle(
        color: AppColors.fg0,
        fontWeight: FontWeight.w800,
        fontSize: 20,
        letterSpacing: 3.2,
      ),
    );
  }
}

class _SchedulePill extends StatelessWidget {
  const _SchedulePill();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.accentSoft,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: const Color(0x7322D3EE)),
      ),
      child: const Text(
        'FIFA WORLD CUP 2026',
        style: TextStyle(
          color: AppColors.accent,
          fontWeight: FontWeight.w700,
          fontSize: 13,
          letterSpacing: 2.0,
        ),
      ),
    );
  }
}

class _HeroTitle extends StatelessWidget {
  const _HeroTitle();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: const [
        Text(
          '32개국 64경기를 한 화면에',
          style: TextStyle(
            color: AppColors.fg0,
            fontWeight: FontWeight.w800,
            fontSize: 36,
            height: 1.1,
            letterSpacing: -0.5,
          ),
        ),
        Text(
          '축구 월드컵 일정·결과',
          style: TextStyle(
            color: AppColors.accent,
            fontWeight: FontWeight.w800,
            fontSize: 36,
            height: 1.1,
            letterSpacing: -0.5,
          ),
        ),
        Text(
          '& 라이브 매치 안내',
          style: TextStyle(
            color: AppColors.fg0,
            fontWeight: FontWeight.w800,
            fontSize: 36,
            height: 1.1,
            letterSpacing: -0.5,
          ),
        ),
      ],
    );
  }
}

class _ActionButtons extends StatelessWidget {
  const _ActionButtons({required this.onTap});

  final void Function(BuildContext context, String label) onTap;

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        ElevatedButton(
          onPressed: () => onTap(context, '오늘의 경기'),
          style: ElevatedButton.styleFrom(
            backgroundColor: AppColors.accent,
            foregroundColor: const Color(0xFF04131A),
            padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 16),
            shape: const StadiumBorder(),
            textStyle: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 15,
            ),
          ),
          child: const Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('오늘의 경기'),
              SizedBox(width: 8),
              Icon(Icons.arrow_forward, size: 18),
            ],
          ),
        ),
        OutlinedButton(
          onPressed: () => onTap(context, '전체 일정 보기'),
          style: OutlinedButton.styleFrom(
            foregroundColor: AppColors.fg0,
            side: const BorderSide(color: Color(0x38FFFFFF)),
            padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 16),
            shape: const StadiumBorder(),
            textStyle: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 15,
            ),
          ),
          child: const Text('전체 일정 보기'),
        ),
        OutlinedButton(
          onPressed: () => onTap(context, '자유게시판·건의'),
          style: OutlinedButton.styleFrom(
            foregroundColor: AppColors.fg0,
            side: const BorderSide(color: Color(0x38FFFFFF)),
            padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 16),
            shape: const StadiumBorder(),
            textStyle: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 15,
            ),
          ),
          child: const Text('자유게시판·건의'),
        ),
      ],
    );
  }
}

class _ChipList extends StatelessWidget {
  const _ChipList();

  static const _chips = [
    '예측·P',
    'AI 분석',
    '본선',
    '조 편성',
    '16강',
    '8강',
    '라이브 스코어',
    '골 순위',
    '하이라이트',
    '응원단',
    '통계',
  ];

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final label in _chips)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            decoration: BoxDecoration(
              color: AppColors.chipBg,
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: AppColors.chipBorder),
            ),
            child: Text(
              label,
              style: const TextStyle(
                color: AppColors.fg1,
                fontSize: 13,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
      ],
    );
  }
}
