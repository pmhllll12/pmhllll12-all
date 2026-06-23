import 'package:flutter_test/flutter_test.dart';

import 'package:pmh_flutter_application_1/main.dart';

void main() {
  testWidgets('IntroScreen renders hero title and pill', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const WorldCupApp());

    expect(find.text('WORLDCUP'), findsOneWidget);
    expect(find.text('FIFA WORLD CUP 2026'), findsOneWidget);
    expect(find.text('축구 월드컵 일정·결과'), findsOneWidget);
    expect(find.text('오늘의 경기'), findsWidgets);
  });
}
