import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

import '../../../../core/models/backend_catalog.dart';
import '../../../../core/network/http_client.dart';
import '../../../../core/providers/catalog_providers.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';

class AiLoadoutScreen extends ConsumerStatefulWidget {
  const AiLoadoutScreen({super.key});

  @override
  ConsumerState<AiLoadoutScreen> createState() => _AiLoadoutScreenState();
}

class _AiLoadoutScreenState extends ConsumerState<AiLoadoutScreen> {
  final ImagePicker _picker = ImagePicker();
  bool _isAnalyzing = false;
  String? _inferenceError;
  AiInferenceResult? _inference;

  Future<void> _pickAndAnalyze() async {
    setState(() {
      _isAnalyzing = true;
      _inferenceError = null;
      _inference = null;
    });
    try {
      final image = await _picker.pickImage(source: ImageSource.gallery);
      if (image == null) return;
      final bytes = await image.readAsBytes();
      final contentType = _imageContentType(bytes);
      final result = await ref
          .read(aeroCloudClientProvider)
          .inferImage(bytes, contentType: contentType);
      if (mounted) setState(() => _inference = result);
    } on AeroCloudException catch (error) {
      if (mounted) setState(() => _inferenceError = error.message);
    } on Exception catch (error) {
      if (mounted) setState(() => _inferenceError = error.toString());
    } finally {
      if (mounted) setState(() => _isAnalyzing = false);
    }
  }

  String _imageContentType(Uint8List bytes) {
    if (bytes.length >= 3 &&
        bytes[0] == 0xff &&
        bytes[1] == 0xd8 &&
        bytes[2] == 0xff) {
      return 'image/jpeg';
    }
    if (bytes.length >= 8 &&
        bytes[0] == 0x89 &&
        bytes[1] == 0x50 &&
        bytes[2] == 0x4e &&
        bytes[3] == 0x47 &&
        bytes[4] == 0x0d &&
        bytes[5] == 0x0a &&
        bytes[6] == 0x1a &&
        bytes[7] == 0x0a) {
      return 'image/png';
    }
    if (bytes.length >= 12 &&
        String.fromCharCodes(bytes.sublist(0, 4)) == 'RIFF' &&
        String.fromCharCodes(bytes.sublist(8, 12)) == 'WEBP') {
      return 'image/webp';
    }
    throw const AeroCloudException(
      'Choose a JPEG, PNG, or WebP image to run inference.',
    );
  }

  @override
  Widget build(BuildContext context) {
    final ref = this.ref;
    final inventory = ref.watch(aiInventoryProvider);
    return TacticalAppScaffold(
      title: 'Edge AI Loadout',
      actions: [
        IconButton(
          tooltip: 'Refresh model inventory',
          onPressed: () => ref.invalidate(aiInventoryProvider),
          icon: const Icon(Icons.refresh),
        ),
      ],
      child: inventory.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _CatalogMessage(
          icon: Icons.cloud_off,
          title: 'Model inventory unavailable',
          detail: error.toString(),
        ),
        data: (result) => Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _CatalogNote(
              mode: result.mode,
              note: result.note,
              routerStatus: result.routerStatus,
            ),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerLeft,
              child: FilledButton.icon(
                onPressed: _isAnalyzing ? null : _pickAndAnalyze,
                icon: _isAnalyzing
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Icon(Icons.image_search),
                label: Text(
                  _isAnalyzing
                      ? 'Analyzing image…'
                      : 'Choose image and analyze',
                ),
              ),
            ),
            if (_inferenceError case final error?) ...[
              const SizedBox(height: 8),
              _InferenceError(error: error),
            ],
            const SizedBox(height: 8),
            Expanded(
              child: ListView(
                children: [
                  if (_inference case final inference?)
                    _InferenceResultCard(result: inference),
                  if (result.models.isEmpty)
                    const _CatalogMessage(
                      icon: Icons.memory,
                      title: 'No models reported',
                      detail: 'The backend has no model inventory to display.',
                    )
                  else
                    ...result.models.map((model) => _ModelTile(model: model)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _InferenceError extends StatelessWidget {
  const _InferenceError({required this.error});

  final String error;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(padding: const EdgeInsets.all(12), child: Text(error)),
    );
  }
}

class _InferenceResultCard extends StatelessWidget {
  const _InferenceResultCard({required this.result});

  final AiInferenceResult result;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Inference · ${result.missionName}',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            Text(
              'Router ${result.routerLabel} · '
              '${(result.routerConfidence * 100).toStringAsFixed(1)}%',
            ),
            const Divider(),
            for (final stage in result.stages)
              ListTile(
                contentPadding: EdgeInsets.zero,
                dense: true,
                title: Text(stage.stageName),
                subtitle: Text(
                  stage.status == 'skipped'
                      ? 'Skipped by mission conditions'
                      : '${stage.label} · '
                            '${((stage.confidence ?? 0) * 100).toStringAsFixed(1)}%',
                ),
                trailing: Text(stage.status.toUpperCase()),
              ),
          ],
        ),
      ),
    );
  }
}

class _CatalogNote extends StatelessWidget {
  const _CatalogNote({
    required this.mode,
    required this.note,
    required this.routerStatus,
  });

  final String mode;
  final String note;
  final String routerStatus;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.memory, color: TacticalColors.warning),
                const SizedBox(width: 12),
                Expanded(child: Text(note)),
                const SizedBox(width: 8),
                Chip(label: Text(mode.toUpperCase())),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Mission router: $routerStatus',
              style: const TextStyle(color: TacticalColors.muted),
            ),
          ],
        ),
      ),
    );
  }
}

class _ModelTile extends StatelessWidget {
  const _ModelTile({required this.model});

  final AiModelSummary model;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.psychology_outlined),
        title: Text(model.name),
        subtitle: Text(
          '${model.task} · ${model.version} · ${model.stageCount} stages',
        ),
        trailing: Chip(label: Text(model.status)),
      ),
    );
  }
}

class _CatalogMessage extends StatelessWidget {
  const _CatalogMessage({
    required this.icon,
    required this.title,
    required this.detail,
  });

  final IconData icon;
  final String title;
  final String detail;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: TacticalColors.warning, size: 42),
              const SizedBox(height: 12),
              Text(title, style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              Text(
                detail,
                textAlign: TextAlign.center,
                style: const TextStyle(color: TacticalColors.muted),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
