class UserModel {
  final String id;
  final String email;
  final String? fullName;
  final String role;
  final bool isActive;
  final bool isVerified;
  final bool isApproved;
  final DateTime? lastActive;
  final DateTime createdAt;

  UserModel({
    required this.id,
    required this.email,
    this.fullName,
    required this.role,
    required this.isActive,
    required this.isVerified,
    required this.isApproved,
    this.lastActive,
    required this.createdAt,
  });

  // Getter aliases for convenience
  String get name => fullName ?? email.split('@').first;
  bool get isAdmin => role.toLowerCase() == 'admin' || role.toLowerCase() == 'superadmin';

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? json['name'],
      role: json['role'] ?? 'user',
      isActive: json['is_active'] ?? json['isActive'] ?? false,
      isVerified: json['is_verified'] ?? json['isVerified'] ?? false,
      isApproved: json['is_approved'] ?? json['isApproved'] ?? false,
      lastActive: json['last_active'] != null ? DateTime.tryParse(json['last_active'].toString()) : null,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at'].toString()) : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'full_name': fullName,
        'role': role,
        'is_active': isActive,
        'is_verified': isVerified,
        'is_approved': isApproved,
        'last_active': lastActive?.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
      };
}