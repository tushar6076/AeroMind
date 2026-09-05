import 'dart:io';
import 'package:flutter/foundation.dart';

class ApiEndpoints {
  /// Production API exposed through Cloudflare Tunnel.
  static const String productionHost = 'aeromind.hacksmiths.dev';

  /// Whether the application should use the local FastAPI server.
  ///
  /// Keep this false for normal/production builds.
  /// Set it to true when developing against localhost.
  static const bool useLocalApi = false;

  /// Resolve the API host dynamically.
  static String get _host {
    if (!useLocalApi) {
      return productionHost;
    }

    if (kIsWeb) {
      return 'localhost:8000';
    }

    if (Platform.isAndroid) {
      // Android Emulator -> host machine localhost
      return '10.0.2.2:8000';
    }

    if (Platform.isIOS) {
      // iOS Simulator -> host machine localhost
      return 'localhost:8000';
    }

    // macOS / desktop development
    return '127.0.0.1:8000';
  }

  /// API protocol.
  static String get _httpScheme => useLocalApi ? 'http' : 'https';

  /// WebSocket protocol.
  static String get _wsScheme => useLocalApi ? 'ws' : 'wss';

  /// Base REST API URL.
  static String get baseUrl => '$_httpScheme://$_host';

  /// Uplink WebSocket endpoint (App <-> Drone live sync).
  static String uplinkWs(String clientId) =>
      '$_wsScheme://$_host/telemetry/uplink/$clientId';

  // ==========================================
  // Auth Routes
  // ==========================================
  static const String login = '/auth/login';
  static const String signup = '/auth/signup';
  static const String refreshToken = '/auth/token/refresh';
  static const String verifyToken = '/auth/token/verify';
  static const String forgotPassword = '/auth/forgot-password';
  static const String verifyOtp = '/auth/verify-otp';
  static const String resetPassword = '/auth/reset-password';

  // ==========================================
  // Connection & Control Lock Routes
  // ==========================================
  static const String connectionRequest = '/connection/request';
  static const String connectionStatus = '/connection/status';
  static const String connectionIsBusy = '/connection/is-busy';
  static const String connectionDisconnect = '/connection/disconnect';
  static const String connectionHistory = '/connection/history';

  // ==========================================
  // Drone Commands (Flight, Manual & Media)
  // ==========================================
  // Flight basic controls
  static const String takeoff = '/drone/command/flight/takeoff';
  static const String land = '/drone/command/flight/land';
  static const String rtl = '/drone/command/flight/rtl';
  static const String hover = '/drone/command/flight/hover';
  static const String emergencyStop = '/drone/command/flight/emergency-stop';

  // Joystick manual controls
  static const String joystickLeft = '/drone/command/manual/joystick/left';
  static const String joystickRight = '/drone/command/manual/joystick/right';

  // Media & Peripherals
  static const String cameraStart = '/drone/command/camera/start';
  static const String cameraStop = '/drone/command/camera/stop';
  static const String lightsToggle = '/drone/command/lights';

  // ==========================================
  // Telemetry & WebRTC Streaming Routes
  // ==========================================
  static const String telemetryLatest = '/drone/telemetry/latest';
  static String telemetryByDroneId(String droneId) =>
      '/drone/telemetry/latest/$droneId';

  static const String streamOffer = '/stream/offer';
  static const String streamAnswer = '/stream/answer';
  static const String streamIceCandidate = '/stream/ice-candidate';
  static const String streamEnd = '/stream/end';

  // ==========================================
  // AI Model & Intelligence Routes
  // ==========================================
  static const String aiIdentify = '/ai/identify';

  // Active User-Facing Models
  static const String aiActiveModels = '/ai/models/active';
  static String aiActiveModelByKey(String key) => '/ai/models/active/$key';

  // General Model Lookup
  static const String aiAllModels = '/ai/models';
  static String aiModelByKey(String key) => '/ai/models/$key';

  // ==========================================
  // User & Device Management Routes
  // ==========================================
  static const String userProfile = '/users/me';
  static const String changePassword = '/users/change-password';
  static const String logout = '/users/logout';
  static const String deleteAccount = '/users/delete-account';
  static const String userDevices = '/users/devices';
  static String userDeviceById(String deviceId) => '/users/devices/$deviceId';

  // ==========================================
  // Admin Routes
  // ==========================================
  static const String adminUsers = '/admin/users';
  static const String adminPendingUsers = '/admin/users/pending';
  static String adminUserById(String userId) => '/admin/users/$userId';
  static String adminApproveUser(String userId) =>
      '/admin/users/$userId/approve';
  static String adminRejectUser(String userId) => '/admin/users/$userId/reject';
  static String adminDeleteUser(String userId) => '/admin/users/$userId/delete';

  static const String adminActiveController = '/admin/active-controller';
  static const String adminForcedControl = '/admin/forced-control';
  static const String adminReleaseControl = '/admin/release-control';
  static const String adminVerify2Fa = '/admin/verify-2fa';

  // Admin AI Controls
  static String adminToggleAiModel(String modelId) =>
      '/admin/ai/models/$modelId/toggle';
  static const String adminInPlayAiModels = '/admin/ai/models/in-play';
  static String adminRevokeAiModel(String modelKey) =>
      '/admin/ai/models/$modelKey/revoke';
  static const String adminRevokeAllAiModels = '/admin/ai/models/revoke-all';
}