class TelemetryModel {
  final double altitude;
  final double speed;
  final double latitude;
  final double longitude;
  final int batteryLevel;
  final bool isCameraActive;
  final String flightMode;

  TelemetryModel({
    this.altitude = 0.0,
    this.speed = 0.0,
    this.latitude = 0.0,
    this.longitude = 0.0,
    this.batteryLevel = 100,
    this.isCameraActive = false,
    this.flightMode = 'Manual',
  });

  factory TelemetryModel.fromJson(Map<String, dynamic> json) {
    return TelemetryModel(
      altitude: (json['altitude'] ?? 0.0).toDouble(),
      speed: (json['speed'] ?? 0.0).toDouble(),
      latitude: (json['latitude'] ?? 0.0).toDouble(),
      longitude: (json['longitude'] ?? 0.0).toDouble(),
      batteryLevel: json['battery'] ?? 100,
      isCameraActive: json['is_camera_active'] ?? false,
      flightMode: json['flight_mode'] ?? 'Manual',
    );
  }
}