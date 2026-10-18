class AiModelSummary {
  const AiModelSummary({
    required this.id,
    required this.name,
    required this.version,
    required this.task,
    required this.status,
    required this.stageCount,
  });

  final String id;
  final String name;
  final String version;
  final String task;
  final String status;
  final int stageCount;

  factory AiModelSummary.fromJson(Map<String, dynamic> json) {
    return AiModelSummary(
      id: json['id'] as String,
      name: json['name'] as String,
      version: json['version'] as String,
      task: json['task'] as String,
      status: json['status'] as String,
      stageCount: json['stage_count'] as int,
    );
  }
}

class AiInventory {
  const AiInventory({
    required this.mode,
    required this.note,
    required this.routerStatus,
    required this.models,
  });

  final String mode;
  final String note;
  final String routerStatus;
  final List<AiModelSummary> models;

  factory AiInventory.fromJson(Map<String, dynamic> json) {
    return AiInventory(
      mode: json['mode'] as String,
      note: json['note'] as String,
      routerStatus: json['router_status'] as String,
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

class AiStagePrediction {
  const AiStagePrediction({
    required this.stageId,
    required this.stageName,
    required this.task,
    required this.status,
    required this.label,
    required this.confidence,
  });

  final String stageId;
  final String stageName;
  final String task;
  final String status;
  final String? label;
  final double? confidence;

  factory AiStagePrediction.fromJson(Map<String, dynamic> json) {
    return AiStagePrediction(
      stageId: json['stage_id'] as String,
      stageName: json['stage_name'] as String,
      task: json['task'] as String,
      status: json['status'] as String,
      label: json['label'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble(),
    );
  }
}

class AiInferenceResult {
  const AiInferenceResult({
    required this.missionId,
    required this.missionName,
    required this.routerLabel,
    required this.routerConfidence,
    required this.stages,
  });

  final String missionId;
  final String missionName;
  final String routerLabel;
  final double routerConfidence;
  final List<AiStagePrediction> stages;

  factory AiInferenceResult.fromJson(Map<String, dynamic> json) {
    return AiInferenceResult(
      missionId: json['mission_id'] as String,
      missionName: json['mission_name'] as String,
      routerLabel: json['router_label'] as String,
      routerConfidence: (json['router_confidence'] as num).toDouble(),
      stages: (json['stages'] as List<dynamic>)
          .map(
            (stage) => AiStagePrediction.fromJson(
              Map<String, dynamic>.from(stage as Map),
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
