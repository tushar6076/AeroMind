import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:aero_app/app.dart';
import 'package:aero_app/core/models/backend_catalog.dart';
import 'package:aero_app/core/providers/catalog_providers.dart';
import 'package:aero_app/core/services/connection_store.dart';
import 'package:aero_app/features/edge_ai/presentation/screens/ai_loadout_screen.dart';
import 'package:aero_app/features/settings/presentation/screens/rig_settings_screen.dart';
import 'package:aero_app/features/vault/presentation/screens/recon_vault_screen.dart';

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

  testWidgets('lobby docks stay beside the aircraft without scrolling', (
    WidgetTester tester,
  ) async {
    tester.view.physicalSize = const Size(720, 500);
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
    await tester.pumpAndSettle();

    expect(find.byType(SingleChildScrollView), findsNothing);
    final aircraft = tester.getRect(find.byIcon(Icons.airplanemode_active));
    expect(
      tester.getRect(find.text('FLIGHT MODES')).center.dx,
      lessThan(aircraft.center.dx),
    );
    expect(
      tester.getRect(find.text('RECON VAULT')).center.dx,
      greaterThan(aircraft.center.dx),
    );
    expect(tester.takeException(), isNull);

    tester.view.physicalSize = const Size(640, 360);
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          connectionStoreProvider.overrideWithValue(_MemoryConnectionStore()),
        ],
        child: const AeroMindApp(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.byType(SingleChildScrollView), findsNothing);
    final compactAircraft = tester.getRect(
      find.byIcon(Icons.airplanemode_active),
    );
    expect(
      tester
          .getRect(find.byTooltip('Flight modes · Operational profile'))
          .center
          .dx,
      lessThan(compactAircraft.center.dx),
    );
    expect(
      tester.getRect(find.byTooltip('Recon vault · Local media')).center.dx,
      greaterThan(compactAircraft.center.dx),
    );
    await tester.tap(find.byTooltip('Flight modes · Operational profile'));
    await tester.pumpAndSettle();
    expect(find.text('Flight Mode Hub'), findsOneWidget);
    expect(tester.takeException(), isNull);
  });

  testWidgets('AI loadout renders the backend-provided model catalog', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          aiInventoryProvider.overrideWith(
            (ref) async => const AiInventory(
              mode: 'missions',
              note: 'Catalog supplied by the backend.',
              routerStatus: 'Router unavailable',
              models: [
                AiModelSummary(
                  id: 'test',
                  name: 'Test detector',
                  version: 'test',
                  task: 'Object detection',
                  status: 'Ready',
                  stageCount: 1,
                ),
              ],
            ),
          ),
        ],
        child: const MaterialApp(home: AiLoadoutScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Catalog supplied by the backend.'), findsOneWidget);
    expect(find.text('Mission router: Router unavailable'), findsOneWidget);
    expect(find.text('Test detector'), findsOneWidget);
    expect(find.text('Choose image and analyze'), findsOneWidget);
    expect(find.text('Vision detector'), findsNothing);
  });

  testWidgets('recon vault renders the backend-provided media catalog', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          vaultInventoryProvider.overrideWith(
            (ref) async => const VaultInventory(
              mode: 'demo',
              note: 'Media inventory supplied by the backend.',
              items: [
                VaultItem(
                  id: 'test-image',
                  title: 'Test image',
                  mediaType: 'image',
                  capturedAt: null,
                  durationSeconds: null,
                  sizeBytes: null,
                ),
              ],
            ),
          ),
        ],
        child: const MaterialApp(home: ReconVaultScreen()),
      ),
    );
    await tester.pumpAndSettle();

    expect(
      find.text('Media inventory supplied by the backend.'),
      findsOneWidget,
    );
    expect(find.text('Test image'), findsOneWidget);
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
