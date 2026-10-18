import 'dart:async';
import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;

import '../constants/api_endpoints.dart';
import '../constants/default_configs.dart';
import '../models/backend_catalog.dart';
import '../models/backend_status.dart';
import '../services/backend_connection.dart';

class AeroCloudException implements Exception {
  const AeroCloudException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}

class AeroCloudClient {
  AeroCloudClient({required this.connection, http.Client? client})
    : _client = client ?? http.Client();

  final BackendConnection? connection;
  final http.Client _client;

  bool get isConfigured => connection != null;

  Future<BackendHealth> getHealth() async {
    final json = await _get(ApiEndpoints.systemHealth);
    return BackendHealth.fromJson(json);
  }

  Future<FlightStatus> getFlightStatus() async {
    final json = await _get(ApiEndpoints.flightStatus);
    return FlightStatus.fromJson(json);
  }

  Future<AiInventory> getAiInventory() async {
    final json = await _get(ApiEndpoints.aiLoadout);
    return AiInventory.fromJson(json);
  }

  Future<VaultInventory> getVaultInventory() async {
    final json = await _get(ApiEndpoints.vaultItems);
    return VaultInventory.fromJson(json);
  }

  Future<FlightStatus> selectFlightMode(String mode) async {
    final json = await _post(ApiEndpoints.flightMode, {'mode': mode});
    return FlightStatus.fromJson(json);
  }

  Future<FlightStatus> startFlightSession() async {
    final json = await _post(ApiEndpoints.flightSession, const {});
    return FlightStatus.fromJson(json);
  }

  Future<FlightStatus> endFlightSession() async {
    final json = await _delete(ApiEndpoints.flightSession);
    return FlightStatus.fromJson(json);
  }

  Future<FlightStatus> arm() async {
    final json = await _post(ApiEndpoints.flightArm, const {});
    return FlightStatus.fromJson(json);
  }

  Future<FlightStatus> disarm() async {
    final json = await _post(ApiEndpoints.flightDisarm, const {});
    return FlightStatus.fromJson(json);
  }

  Future<void> sendControl({
    required double roll,
    required double pitch,
    required double yaw,
    required double throttle,
  }) async {
    await _send(
      'POST',
      ApiEndpoints.flightControl,
      body: {'roll': roll, 'pitch': pitch, 'yaw': yaw, 'throttle': throttle},
      authenticated: true,
      expectBody: false,
    );
  }

  Future<Map<String, dynamic>> createVideoAnswer({
    required String sdp,
    required String type,
  }) {
    return _post(ApiEndpoints.videoOffer, {'sdp': sdp, 'type': type});
  }

  Uri telemetrySocketUri() {
    final configured = _requireConnection();
    return configured.baseUri.replace(
      scheme: configured.baseUri.scheme == 'https' ? 'wss' : 'ws',
      path: ApiEndpoints.telemetrySocket,
      query: null,
      fragment: null,
    );
  }

  Uri flightControlSocketUri() {
    final configured = _requireConnection();
    final token = configured.accessToken;
    if (token == null || token.isEmpty) {
      throw const AeroCloudException(
        'Set the Aero Cloud access token in Link Details before using controls.',
      );
    }
    return configured.baseUri.replace(
      scheme: configured.baseUri.scheme == 'https' ? 'wss' : 'ws',
      path: ApiEndpoints.flightControlSocket,
      query: null,
      fragment: null,
    );
  }

  String get controlSocketProtocol {
    final configured = _requireConnection();
    final token = configured.accessToken;
    if (token == null || token.isEmpty) {
      throw const AeroCloudException(
        'Set the Aero Cloud access token in Link Details before using controls.',
      );
    }
    return 'aeromind-auth-${base64Url.encode(utf8.encode(token)).replaceAll('=', '')}';
  }

  Future<Map<String, dynamic>> _get(String path) =>
      _send('GET', path, authenticated: false);

  Future<Map<String, dynamic>> _post(String path, Map<String, Object?> body) {
    return _send('POST', path, body: body, authenticated: true);
  }

  Future<Map<String, dynamic>> _delete(String path) =>
      _send('DELETE', path, authenticated: true);

  Future<Map<String, dynamic>> _send(
    String method,
    String path, {
    Map<String, Object?>? body,
    bool authenticated = false,
    bool expectBody = true,
  }) async {
    final configured = _requireConnection();
    final headers = <String, String>{'Accept': 'application/json'};
    if (body != null) headers['Content-Type'] = 'application/json';
    if (authenticated) {
      final token = configured.accessToken;
      if (token == null || token.isEmpty) {
        throw const AeroCloudException(
          'Set the Aero Cloud access token in Link Details before using controls.',
        );
      }
      headers['Authorization'] = 'Bearer $token';
    }

    final uri = configured.baseUri.resolve(path);
    late final http.Response response;
    try {
      response = switch (method) {
        'GET' =>
          await _client
              .get(uri, headers: headers)
              .timeout(DefaultConfigs.requestTimeout),
        'POST' =>
          await _client
              .post(uri, headers: headers, body: jsonEncode(body))
              .timeout(DefaultConfigs.requestTimeout),
        'DELETE' =>
          await _client
              .delete(uri, headers: headers)
              .timeout(DefaultConfigs.requestTimeout),
        _ => throw StateError('Unsupported HTTP method: $method'),
      };
    } on TimeoutException {
      throw AeroCloudException('Aero Cloud request timed out: $uri');
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw AeroCloudException(
        _errorMessage(response),
        statusCode: response.statusCode,
      );
    }
    if (!expectBody || response.body.isEmpty) return const {};
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is! Map) {
        throw const FormatException('Expected a JSON object response');
      }
      return Map<String, dynamic>.from(decoded);
    } on FormatException catch (error) {
      throw AeroCloudException('Invalid response from Aero Cloud: $error');
    }
  }

  String _errorMessage(http.Response response) {
    try {
      final decoded = jsonDecode(response.body);
      if (decoded is Map) {
        final detail = decoded['detail'];
        if (detail is String) return detail;
        if (detail is Map && detail['message'] is String) {
          return detail['message'] as String;
        }
      }
    } on FormatException {
      return 'Aero Cloud returned HTTP ${response.statusCode}.';
    }
    return 'Aero Cloud returned HTTP ${response.statusCode}.';
  }

  BackendConnection _requireConnection() {
    final configured = connection;
    if (configured == null) {
      throw const AeroCloudException(
        'Backend address is not configured. Set it in Link Details.',
      );
    }
    return configured;
  }

  void close() => _client.close();
}

final aeroCloudClientProvider = Provider<AeroCloudClient>((ref) {
  final settings = ref.watch(backendConnectionProvider).asData?.value;
  final client = AeroCloudClient(connection: settings);
  ref.onDispose(client.close);
  return client;
});
