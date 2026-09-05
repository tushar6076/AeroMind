import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_provider.dart';
import '../models/user_model.dart';

final pendingUsersProvider = FutureProvider<List<UserModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final List response = await apiService.getPendingUsers();
  return response.map((e) => UserModel.fromJson(e)).toList();
});

class AdminControllerNotifier extends StateNotifier<AsyncValue<void>> {
  final Ref ref;
  AdminControllerNotifier(this.ref) : super(const AsyncValue.data(null));

  Future<bool> forceControlLock(String connectionId) async {
    state = const AsyncValue.loading();
    try {
      await ref.read(apiServiceProvider).forceControlLock(connectionId);
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  Future<bool> releaseControlLock() async {
    state = const AsyncValue.loading();
    try {
      await ref.read(apiServiceProvider).releaseControlLock();
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }
}

final adminControlProvider =
    StateNotifierProvider<AdminControllerNotifier, AsyncValue<void>>((ref) {
  return AdminControllerNotifier(ref);
});