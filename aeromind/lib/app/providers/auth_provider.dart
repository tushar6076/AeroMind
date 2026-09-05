import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'api_provider.dart';
import '../core/services/storage_service.dart';
import '../models/user_model.dart';

final storageServiceProvider = Provider<StorageService>((ref) {
  return StorageService();
});

class AuthState {
  final UserModel? user;
  final String? token;
  final bool isLoading;
  final String? error;

  AuthState({
    this.user,
    this.token,
    this.isLoading = false,
    this.error,
  });

  bool get isAuthenticated => token != null && token!.isNotEmpty;
}

class AuthNotifier extends StateNotifier<AuthState> {
  final Ref ref;

  AuthNotifier(this.ref) : super(AuthState(isLoading: true)) {
    _restoreSession();
  }

  /// Automatically restore token & user profile from local storage on app launch
  Future<void> _restoreSession() async {
    try {
      final storage = ref.read(storageServiceProvider);
      final token = await storage.getToken();
      final cachedUser = await storage.getUserFromLocalDb();

      if (token != null && token.isNotEmpty) {
        final apiService = ref.read(apiServiceProvider);
        apiService.setToken(token);

        // Try restoring fresh profile from remote, fallback to local DB cache
        try {
          final profile = await apiService.getProfile();
          await storage.saveUserToLocalDb(profile);
          state = AuthState(user: profile, token: token, isLoading: false);
        } catch (_) {
          state = AuthState(user: cachedUser, token: token, isLoading: false);
        }
        return;
      }
    } catch (e) {
      state = AuthState(error: e.toString(), isLoading: false);
      return;
    }

    state = AuthState(isLoading: false);
  }

  /// Authenticate user, store secure token, and cache user in SQLite
  Future<bool> login(String email, String password, {String? deviceId, String? deviceInfo}) async {
    state = AuthState(isLoading: true);
    try {
      final apiService = ref.read(apiServiceProvider);
      final storage = ref.read(storageServiceProvider);

      final res = await apiService.login(email, password, deviceId: deviceId, deviceInfo: deviceInfo);
      
      // Handle standard FastAPI error responses or direct access token key
      if (res.containsKey('detail')) {
        state = AuthState(error: res['detail'].toString(), isLoading: false);
        return false;
      }

      final token = res['access_token'] as String?;

      if (token != null) {
        apiService.setToken(token);
        await storage.saveToken(token);

        final profile = await apiService.getProfile();
        await storage.saveUserToLocalDb(profile);

        state = AuthState(user: profile, token: token, isLoading: false);
        return true;
      } else {
        state = AuthState(error: 'Invalid response from server.', isLoading: false);
        return false;
      }
    } catch (e) {
      state = AuthState(error: e.toString(), isLoading: false);
      return false;
    }
  }

  /// Permanently deletes aeromind_local.db & all secure tokens from iOS Simulator storage
  Future<void> logout() async {
    final apiService = ref.read(apiServiceProvider);
    final storage = ref.read(storageServiceProvider);

    apiService.setToken('');
    
    // Purges the aeromind_local.db file and clears FlutterSecureStorage completely
    await storage.deleteEntireDatabase();

    // Reset AuthState so isAuthenticated is false
    state = AuthState(isLoading: false);
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref);
});