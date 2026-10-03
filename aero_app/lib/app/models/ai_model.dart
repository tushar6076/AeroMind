class AiModel {
  final String id;
  final String name;
  final String key;
  final String? description;
  final Map<String, dynamic>? levels;
  final String? provider;
  final bool isActive;

  AiModel({
    required this.id,
    required this.name,
    required this.key,
    this.description,
    this.levels,
    this.provider,
    required this.isActive,
  });

  factory AiModel.fromJson(Map<String, dynamic> json) {
    // Safe conversion for levels map
    Map<String, dynamic>? parsedLevels;
    if (json['levels'] is Map) {
      parsedLevels = Map<String, dynamic>.from(json['levels'] as Map);
    } else if (json['levels'] is List) {
      // If backend sends a List instead of a Map, convert it safely into a Map representation
      final list = json['levels'] as List;
      parsedLevels = {
        for (int i = 0; i < list.length; i++) 'level_$i': list[i]
      };
    }

    return AiModel(
      id: json['id']?.toString() ?? '',
      name: json['name']?.toString() ?? '',
      key: json['key']?.toString() ?? '',
      description: json['description']?.toString(),
      levels: parsedLevels,
      provider: json['provider']?.toString(),
      isActive: json['is_active'] is bool
          ? json['is_active'] as bool
          : (json['is_active'] == 1 || json['is_active'] == 'true'),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'key': key,
      if (description != null) 'description': description,
      if (levels != null) 'levels': levels,
      if (provider != null) 'provider': provider,
      'is_active': isActive,
    };
  }
}