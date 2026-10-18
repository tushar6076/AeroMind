class AiModelSummary {
  const AiModelSummary({
    required this.name,
    required this.version,
    required this.task,
    required this.status,
  });

  final String name;
  final String version;
  final String task;
  final String status;

  factory AiModelSummary.fromJson(Map<String, dynamic> json) {
    return AiModelSummary(
      name: json['name'] as String,
      version: json['version'] as String,
      task: json['task'] as String,
      status: json['status'] as String,
    );
  }
}

class AiInventory {
  const AiInventory({
    required this.mode,
    required this.note,
    required this.models,
  });

  final String mode;
  final String note;
  final List<AiModelSummary> models;

  factory AiInventory.fromJson(Map<String, dynamic> json) {
    return AiInventory(
      mode: json['mode'] as String,
      note: json['note'] as String,
      models: (json['models'] as List<dynamic>)
          .map(
            (model) => AiModelSummary.fromJson(
              Map<String, dynamic>.from(model as Map),
            ),
          )
          .toList(growable: false),
    );
  }
}

class VaultItem {
  const VaultItem({
    required this.id,
    required this.title,
    required this.mediaType,
    required this.capturedAt,
    required this.durationSeconds,
    required this.sizeBytes,
  });

  final String id;
  final String title;
  final String mediaType;
  final DateTime? capturedAt;
  final int? durationSeconds;
  final int? sizeBytes;

  factory VaultItem.fromJson(Map<String, dynamic> json) {
    final capturedAt = json['captured_at'] as String?;
    return VaultItem(
      id: json['id'] as String,
      title: json['title'] as String,
      mediaType: json['media_type'] as String,
      capturedAt: capturedAt == null ? null : DateTime.parse(capturedAt),
      durationSeconds: (json['duration_seconds'] as num?)?.toInt(),
      sizeBytes: (json['size_bytes'] as num?)?.toInt(),
    );
  }
}

class VaultInventory {
  const VaultInventory({
    required this.mode,
    required this.note,
    required this.items,
  });

  final String mode;
  final String note;
  final List<VaultItem> items;

  factory VaultInventory.fromJson(Map<String, dynamic> json) {
    return VaultInventory(
      mode: json['mode'] as String,
      note: json['note'] as String,
      items: (json['items'] as List<dynamic>)
          .map(
            (item) =>
                VaultItem.fromJson(Map<String, dynamic>.from(item as Map)),
          )
          .toList(growable: false),
    );
  }
}
