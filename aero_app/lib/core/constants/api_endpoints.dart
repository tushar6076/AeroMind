abstract final class ApiEndpoints {
  static const apiPrefix = '/api/v1';
  static const systemStatus = '$apiPrefix/system/status';
  static const systemHealth = '$apiPrefix/system/health';
  static const flightStatus = '$apiPrefix/flight/status';
  static const flightMode = '$apiPrefix/flight/mode';
  static const flightSession = '$apiPrefix/flight/session';
  static const flightArm = '$apiPrefix/flight/arm';
  static const flightDisarm = '$apiPrefix/flight/disarm';
  static const flightControl = '$apiPrefix/flight/control';
  static const flightControlSocket = '$apiPrefix/flight/control/ws';
  static const telemetrySocket = '$apiPrefix/telemetry/ws';
  static const videoOffer = '$apiPrefix/video/offer';
  static const aiLoadout = '$apiPrefix/ai/loadout';
  static const aiInfer = '$apiPrefix/ai/infer';
  static const vaultItems = '$apiPrefix/vault/items';
}
