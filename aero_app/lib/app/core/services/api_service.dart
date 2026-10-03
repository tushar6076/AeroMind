import 'dart:convert';
import 'package:http/http.dart' as http;
import '../constants/api_endpoints.dart';
import '../../models/user_model.dart';
import '../../models/ai_model.dart';

class ApiService {
  String? _authToken;

  void setToken(String token) {
    _authToken = token;
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  // ==========================================
  // Auth & Profile Routes
  // ==========================================
  Future<Map<String, dynamic>> register(
    String email,
    String password, {
    String? fullName,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.signup}'),
      headers: _headers,
      body: jsonEncode({
        'email': email,
        'password': password,
        'full_name': ?fullName,
      }),
    );

    final Map<String, dynamic> data = jsonDecode(response.body);

    if (response.statusCode >= 400) {
      throw Exception(data['detail'] ?? 'Registration failed (${response.statusCode})');
    }

    return data;
  }

  Future<Map<String, dynamic>> login(
    String email, 
    String password, {
    String? deviceId,
    String? deviceInfo,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.login}'),
      headers: _headers,
      body: jsonEncode({
        'email': email,
        'password': password,
        'device_id': deviceId ?? 'mobile-app-client',
        'device_info': deviceInfo ?? 'Flutter Client',
      }),
    );

    final Map<String, dynamic> data = jsonDecode(response.body);

    if (response.statusCode >= 400) {
      throw Exception(data['detail'] ?? 'Authentication failed (${response.statusCode})');
    }

    return data;
  }

  Future<Map<String, dynamic>> requestPasswordReset(String email) async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.forgotPassword}'),
      headers: _headers,
      body: jsonEncode({'email': email}),
    );

    final Map<String, dynamic> data = jsonDecode(response.body);

    if (response.statusCode >= 400) {
      throw Exception(data['detail'] ?? 'Failed to request password reset (${response.statusCode})');
    }

    return data;
  }

  Future<Map<String, dynamic>> resetPassword({
    required String email,
    required String code,
    required String newPassword,
  }) async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.resetPassword}'),
      headers: _headers,
      body: jsonEncode({
        'email': email,
        'code': code,
        'new_password': newPassword,
      }),
    );

    final Map<String, dynamic> data = jsonDecode(response.body);

    if (response.statusCode >= 400) {
      throw Exception(data['detail'] ?? 'Password reset failed (${response.statusCode})');
    }

    return data;
  }

  Future<UserModel> getProfile() async {
    final response = await http.get(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.userProfile}'),
      headers: _headers,
    );
    return UserModel.fromJson(jsonDecode(response.body));
  }

  // ==========================================
  // Connection Routes
  // ==========================================
  Future<Map<String, dynamic>> requestConnection() async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.connectionRequest}'),
      headers: _headers,
    );
    return jsonDecode(response.body);
  }

  Future<bool> disconnectConnection() async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.connectionDisconnect}'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  // ==========================================
  // Admin Routes
  // ==========================================
  Future<List<dynamic>> getPendingUsers() async {
    final response = await http.get(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.adminPendingUsers}'),
      headers: _headers,
    );
    return jsonDecode(response.body);
  }

  Future<bool> forceControlLock(String connectionId) async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.adminForcedControl}'),
      headers: _headers,
      body: jsonEncode({'connection_id': connectionId}),
    );
    return response.statusCode == 200;
  }

  Future<bool> releaseControlLock() async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.adminReleaseControl}'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  // ==========================================
  // AI Models Routes
  // ==========================================
  Future<List<AiModel>> getActiveAiModels() async {
    final response = await http.get(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.aiActiveModels}'),
      headers: _headers,
    );
    final dynamic decoded = jsonDecode(response.body);
    final List list = decoded is List
        ? decoded
        : (decoded['models'] ?? decoded['data'] ?? []);

    return list
        .map((item) => AiModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<List<AiModel>> getInPlayAiModels() async {
    final response = await http.get(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.adminInPlayAiModels}'),
      headers: _headers,
    );
    final dynamic decoded = jsonDecode(response.body);
    final List list = decoded is List
        ? decoded
        : (decoded['models'] ?? decoded['data'] ?? []);

    return list
        .map((item) => AiModel.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<bool> toggleAiModel(String modelId) async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.adminToggleAiModel(modelId)}'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  Future<bool> revokeAiModel(String modelKey) async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.adminRevokeAiModel(modelKey)}'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  Future<bool> revokeAllAiModels() async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.adminRevokeAllAiModels}'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  // ==========================================
  // Device Routes
  // ==========================================
  Future<List<dynamic>> getDevices() async {
    final response = await http.get(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.userDevices}'),
      headers: _headers,
    );
    return jsonDecode(response.body);
  }

  Future<bool> deleteDevice(String deviceId) async {
    final response = await http.delete(
      Uri.parse('${ApiEndpoints.baseUrl}${ApiEndpoints.userDeviceById(deviceId)}'),
      headers: _headers,
    );
    return response.statusCode == 200;
  }

  // ==========================================
  // Logs & Requests Routes
  // ==========================================
  Future<List<dynamic>> getAdminLogs({String? targetId}) async {
    final uri = Uri.parse('${ApiEndpoints.baseUrl}/admin/logs').replace(
      queryParameters: targetId != null ? {'target_id': targetId} : null,
    );
    final response = await http.get(uri, headers: _headers);
    return jsonDecode(response.body);
  }

  Future<List<dynamic>> getAiRequests() async {
    final response = await http.get(
      Uri.parse('${ApiEndpoints.baseUrl}/ai/requests'),
      headers: _headers,
    );
    return jsonDecode(response.body);
  }

  // ==========================================
  // Flight Commands
  // ==========================================
  Future<bool> sendFlightCommand(String endpoint, {Map<String, dynamic>? payload}) async {
    final response = await http.post(
      Uri.parse('${ApiEndpoints.baseUrl}$endpoint'),
      headers: _headers,
      body: payload != null ? jsonEncode(payload) : null,
    );
    return response.statusCode >= 200 && response.statusCode < 300;
  }
}