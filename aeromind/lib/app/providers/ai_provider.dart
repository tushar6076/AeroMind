import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/ai_model.dart';
import 'api_provider.dart';

final activeAiModelsProvider = FutureProvider<List<AiModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getActiveAiModels();
});

final inPlayAiModelsProvider = FutureProvider<List<AiModel>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getInPlayAiModels();
});

class AiModelManagerNotifier extends StateNotifier<AsyncValue<void>> {
  final Ref ref;

  AiModelManagerNotifier(this.ref) : super(const AsyncValue.data(null));

  void _refreshProviders() {
    ref.invalidate(activeAiModelsProvider);
    ref.invalidate(inPlayAiModelsProvider);
  }

  Future<bool> toggleModel(String modelId) async {
    state = const AsyncValue.loading();
    try {
      await ref.read(apiServiceProvider).toggleAiModel(modelId);
      _refreshProviders();
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  Future<bool> revokeModel(String modelKey) async {
    state = const AsyncValue.loading();
    try {
      await ref.read(apiServiceProvider).revokeAiModel(modelKey);
      _refreshProviders();
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }

  Future<bool> revokeAllModels() async {
    state = const AsyncValue.loading();
    try {
      await ref.read(apiServiceProvider).revokeAllAiModels();
      _refreshProviders();
      state = const AsyncValue.data(null);
      return true;
    } catch (e, st) {
      state = AsyncValue.error(e, st);
      return false;
    }
  }
}

final aiModelManagerProvider =
    StateNotifierProvider<AiModelManagerNotifier, AsyncValue<void>>((ref) {
  return AiModelManagerNotifier(ref);
});