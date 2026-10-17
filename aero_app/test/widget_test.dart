import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:aero_app/app.dart';
import 'package:aero_app/core/services/connection_store.dart';
import 'package:aero_app/features/edge_ai/presentation/screens/ai_loadout_screen.dart';
import 'package:aero_app/features/settings/presentation/screens/rig_settings_screen.dart';

class _MemoryConnectionStore implements ConnectionStore {
  @override
  Future<void> delete(String key) async {}

  @override
  Future<String?> read(String key) async => null;

  @override
  Future<void> write(String key, String value) async {}
}

void main() {
  testWidgets('AeroMind app smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          connectionStoreProvider.overrideWithValue(_MemoryConnectionStore()),
        ],
        child: const AeroMindApp(),
      ),
    );
  });

  testWidgets('lobby deploy flow opens a locked HUD preview', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(1280, 720);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          connectionStoreProvider.overrideWithValue(_MemoryConnectionStore()),
        ],
        child: const AeroMindApp(),
      ),
    );
    expect(find.text('Tactical Lobby'), findsOneWidget);

    await tester.tap(find.text('DEPLOY'));
    await tester.pumpAndSettle();
    expect(find.text('Flight Mode Hub'), findsOneWidget);

    await tester.tap(find.text('CONTINUE'));
    await tester.pumpAndSettle();
    expect(find.text('Pre-flight Diagnostics'), findsOneWidget);
    expect(find.text('ARMING DISABLED · CHECKS NOT PASSED'), findsOneWidget);

    await tester.tap(find.text('PREVIEW HUD'));
    await tester.pumpAndSettle();
    expect(find.text('HUD Preview'), findsOneWidget);
    expect(find.text('PREVIEW ONLY · TRANSMITTER LOCKED'), findsOneWidget);
    expect(find.text('DETECTIONS'), findsOneWidget);
    expect(find.text('0'), findsNothing);
    expect(find.text('CLOSE PREVIEW'), findsOneWidget);
  });

  testWidgets('AI loadout does not display a hardcoded model catalog', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(const MaterialApp(home: AiLoadoutScreen()));

    expect(find.text('AI inventory unavailable'), findsOneWidget);
    expect(find.text('Vision detector'), findsNothing);
  });

  testWidgets('rig settings expose the backend connection monitor', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          connectionStoreProvider.overrideWithValue(_MemoryConnectionStore()),
        ],
        child: const MaterialApp(home: RigSettingsScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('NOT CONFIGURED'), findsOneWidget);
    await tester.tap(find.text('Backend address'));
    await tester.pumpAndSettle();
    expect(find.text('Connection monitor'), findsOneWidget);
  });
}
