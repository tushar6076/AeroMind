import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_provider.dart';

class ConnectionStateModel {
  final bool isConnected;
  final bool isController;
  final String? activeConnectionId;
  final bool isLoading;

  ConnectionStateModel({
    this.isConnected = false,
    this.isController = false,
    this.activeConnectionId,
    this.isLoading = false,
  });
}

class ConnectionNotifier extends StateNotifier<ConnectionStateModel> {
  final Ref ref;

  ConnectionNotifier(this.ref) : super(ConnectionStateModel());

  Future<bool> requestControl() async {
    state = ConnectionStateModel(isLoading: true);
    try {
      final res = await ref.read(apiServiceProvider).requestConnection();
      state = ConnectionStateModel(
        isConnected: true,
        isController: true,
        activeConnectionId: res['connection_id'],
        isLoading: false,
      );
      return true;
    } catch (_) {
      state = ConnectionStateModel(isLoading: false);
      return false;
    }
  }

  Future<void> disconnect() async {
    state = ConnectionStateModel(isLoading: true);
    try {
      await ref.read(apiServiceProvider).disconnectConnection();
    } catch (_) {}
    state = ConnectionStateModel();
  }
}

final connectionProvider =
    StateNotifierProvider<ConnectionNotifier, ConnectionStateModel>((ref) {
  return ConnectionNotifier(ref);
});