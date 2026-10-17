import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/backend_status.dart';
import '../network/http_client.dart';
import '../network/websocket_client.dart';
import '../services/backend_connection.dart';

final backendHealthProvider =
    AsyncNotifierProvider<BackendHealthController, BackendHealth>(
      BackendHealthController.new,
    );

class BackendHealthController extends AsyncNotifier<BackendHealth> {
  Timer? _pollTimer;

  @override
  Future<BackendHealth> build() async {
    await ref.watch(backendConnectionProvider.future);
    final client = ref.watch(aeroCloudClientProvider);
    ref.onDispose(() => _pollTimer?.cancel());
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(
      const Duration(seconds: 3),
      (_) => unawaited(refresh()),
    );
    return client.getHealth();
  }

  Future<void> refresh() async {
    state = await AsyncValue.guard(
      () => ref.read(aeroCloudClientProvider).getHealth(),
    );
  }
}

final flightStatusProvider = FutureProvider.autoDispose<FlightStatus>((ref) {
  return ref.watch(aeroCloudClientProvider).getFlightStatus();
});

final telemetryClientProvider = Provider<AeroCloudWebSocketClient>((ref) {
  return AeroCloudWebSocketClient(ref.watch(aeroCloudClientProvider));
});

final telemetryProvider = StreamProvider.autoDispose<TelemetrySnapshot>((ref) {
  return ref.watch(telemetryClientProvider).telemetry();
});
