import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_provider.dart';
import '../models/device_model.dart';

final userDevicesProvider = FutureProvider<List<DeviceModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final List response = await apiService.getDevices();
  return response.map((e) => DeviceModel.fromJson(e)).toList();
});

class DeviceNotifier extends StateNotifier<AsyncValue<void>> {
  final Ref ref;
  DeviceNotifier(this.ref) : super(const AsyncValue.data(null));

  Future<bool> revokeDevice(String deviceId) async {
    state = const AsyncValue.loading();
    try {
      await ref.read(apiServiceProvider).deleteDevice(deviceId);
      ref.invalidate(userDevicesProvider);
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }
}

final deviceActionProvider =
    StateNotifierProvider<DeviceNotifier, AsyncValue<void>>((ref) {
  return DeviceNotifier(ref);
});