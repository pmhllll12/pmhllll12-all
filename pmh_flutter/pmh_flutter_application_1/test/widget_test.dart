import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:pmh_flutter_application_1/main.dart';

void main() {
  testWidgets('IntroScreen renders hero title and pill', (
    WidgetTester tester,
  ) async {
    // 앱의 첫 화면은 스톱워치로 바뀌었지만 IntroScreen 자체는 그대로 남아 있어
    // 직접 띄워 검증한다.
    await tester.pumpWidget(const MaterialApp(home: IntroScreen()));

    expect(find.text('WORLDCUP'), findsOneWidget);
    expect(find.text('FIFA WORLD CUP 2026'), findsOneWidget);
    expect(find.text('축구 월드컵 일정·결과'), findsOneWidget);
    expect(find.text('오늘의 경기'), findsWidgets);
  });
}
