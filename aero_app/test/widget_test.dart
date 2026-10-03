import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:aero_app/app/app.dart';

void main() {
  testWidgets('AeroMind app smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: AeroMindApp(),
      ),
    );
  });
}