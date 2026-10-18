import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/models/backend_catalog.dart';
import '../../../../core/providers/catalog_providers.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';

class AiLoadoutScreen extends ConsumerWidget {
  const AiLoadoutScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
            _CatalogNote(mode: result.mode, note: result.note),
            const SizedBox(height: 12),
            Expanded(
              child: result.models.isEmpty
                  ? const _CatalogMessage(
                      icon: Icons.memory,
                      title: 'No models reported',
                      detail: 'The backend has no model inventory to display.',
                    )
                  : ListView.separated(
                      itemCount: result.models.length,
                      separatorBuilder: (_, _) => const SizedBox(height: 8),
                      itemBuilder: (context, index) =>
                          _ModelTile(model: result.models[index]),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CatalogNote extends StatelessWidget {
  const _CatalogNote({required this.mode, required this.note});

  final String mode;
  final String note;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.memory, color: TacticalColors.warning),
            const SizedBox(width: 12),
            Expanded(child: Text(note)),
            const SizedBox(width: 8),
            Chip(label: Text(mode.toUpperCase())),
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
        subtitle: Text('${model.task} · ${model.version}'),
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
