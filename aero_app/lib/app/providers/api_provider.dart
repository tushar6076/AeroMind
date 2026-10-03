import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/services/api_service.dart';

/// Provides a single shared instance of ApiService across the app.
final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});