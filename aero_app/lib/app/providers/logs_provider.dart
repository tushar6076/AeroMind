import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_provider.dart';

final adminLogsProvider = FutureProvider.family<List<dynamic>, String?>((ref, targetId) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getAdminLogs(targetId: targetId);
});

final aiRequestsLogsProvider = FutureProvider<List<dynamic>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return await apiService.getAiRequests();
});