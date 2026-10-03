class DeviceModel {
  final String id;
  final String userId;
  final String deviceId;
  final String? deviceInfo;
  final bool isActive;
  final DateTime? lastLogin;

  DeviceModel({
    required this.id,
    required this.userId,
    required this.deviceId,
    this.deviceInfo,
    required this.isActive,
    this.lastLogin,
  });

  factory DeviceModel.fromJson(Map<String, dynamic> json) {
    return DeviceModel(
      id: json['id'],
      userId: json['user_id'],
      deviceId: json['device_id'],
      deviceInfo: json['device_info'],
      isActive: json['is_active'] ?? false,
      lastLogin: json['last_login'] != null ? DateTime.parse(json['last_login']) : null,
    );
  }
}