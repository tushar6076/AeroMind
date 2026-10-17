class ReadinessCheck {
  const ReadinessCheck({
    required this.name,
    required this.ready,
    required this.detail,
  });

  final String name;
  final bool ready;
  final String detail;

  factory ReadinessCheck.fromJson(Map<String, dynamic> json) {
    return ReadinessCheck(
      name: json['name'] as String,
      ready: json['ready'] as bool,
      detail: json['detail'] as String,
    );
  }
}

class BackendHealth {
  const BackendHealth({
    required this.backendOnline,
    required this.elrsConfigured,
    required this.elrsConnected,
    required this.elrsLinkQuality,
    required this.flightControllerTelemetry,
    required this.gpsSatellites,
    required this.batteryPercent,
    required this.imuAvailable,
    required this.companionTemperatureC,
    required this.videoInputConfigured,
    required this.videoInputAvailable,
    required this.videoStreaming,
    required this.readyForFlight,
    required this.checks,
  });

  final bool backendOnline;
  final bool elrsConfigured;
  final bool elrsConnected;
  final int? elrsLinkQuality;
  final bool flightControllerTelemetry;
  final int? gpsSatellites;
  final double? batteryPercent;
  final bool imuAvailable;
  final double? companionTemperatureC;
  final bool videoInputConfigured;
  final bool videoInputAvailable;
  final bool videoStreaming;
  final bool readyForFlight;
  final List<ReadinessCheck> checks;

  factory BackendHealth.fromJson(Map<String, dynamic> json) {
    return BackendHealth(
      backendOnline: json['backend_online'] as bool,
      elrsConfigured: json['elrs_configured'] as bool,
      elrsConnected: json['elrs_connected'] as bool,
      elrsLinkQuality: (json['elrs_link_quality'] as num?)?.toInt(),
      flightControllerTelemetry: json['flight_controller_telemetry'] as bool,
      gpsSatellites: (json['gps_satellites'] as num?)?.toInt(),
      batteryPercent: (json['battery_percent'] as num?)?.toDouble(),
      imuAvailable: json['imu_available'] as bool,
      companionTemperatureC: (json['companion_temperature_c'] as num?)
          ?.toDouble(),
      videoInputConfigured: json['video_input_configured'] as bool,
      videoInputAvailable: json['video_input_available'] as bool,
      videoStreaming: json['video_streaming'] as bool,
      readyForFlight: json['ready_for_flight'] as bool,
      checks: (json['checks'] as List<dynamic>)
          .map(
            (check) => ReadinessCheck.fromJson(
              Map<String, dynamic>.from(check as Map),
            ),
          )
          .toList(growable: false),
    );
  }
}

class FlightStatus {
  const FlightStatus({
    required this.sessionActive,
    required this.armed,
    required this.armingAvailable,
    required this.selectedMode,
    required this.controlAvailable,
    required this.readyForFlight,
    required this.detail,
  });

  final bool sessionActive;
  final bool armed;
  final bool armingAvailable;
  final String? selectedMode;
  final bool controlAvailable;
  final bool readyForFlight;
  final String detail;

  factory FlightStatus.fromJson(Map<String, dynamic> json) {
    return FlightStatus(
      sessionActive: json['session_active'] as bool,
      armed: json['armed'] as bool,
      armingAvailable: json['arming_available'] as bool,
      selectedMode: json['selected_mode'] as String?,
      controlAvailable: json['control_available'] as bool,
      readyForFlight: json['ready_for_flight'] as bool,
      detail: json['detail'] as String,
    );
  }
}

class TelemetrySnapshot {
  const TelemetrySnapshot({
    required this.timestamp,
    this.linkQuality,
    this.batteryVoltage,
    this.batteryPercent,
    this.latitude,
    this.longitude,
    this.gpsSatellites,
    this.rollDegrees,
    this.pitchDegrees,
    this.yawDegrees,
  });

  final double timestamp;
  final int? linkQuality;
  final double? batteryVoltage;
  final double? batteryPercent;
  final double? latitude;
  final double? longitude;
  final int? gpsSatellites;
  final double? rollDegrees;
  final double? pitchDegrees;
  final double? yawDegrees;

  factory TelemetrySnapshot.fromJson(Map<String, dynamic> json) {
    return TelemetrySnapshot(
      timestamp: (json['timestamp'] as num).toDouble(),
      linkQuality: (json['link_quality'] as num?)?.toInt(),
      batteryVoltage: (json['battery_voltage'] as num?)?.toDouble(),
      batteryPercent: (json['battery_percent'] as num?)?.toDouble(),
      latitude: (json['gps_latitude'] as num?)?.toDouble(),
      longitude: (json['gps_longitude'] as num?)?.toDouble(),
      gpsSatellites: (json['gps_satellites'] as num?)?.toInt(),
      rollDegrees: (json['roll_degrees'] as num?)?.toDouble(),
      pitchDegrees: (json['pitch_degrees'] as num?)?.toDouble(),
      yawDegrees: (json['yaw_degrees'] as num?)?.toDouble(),
    );
  }
}
