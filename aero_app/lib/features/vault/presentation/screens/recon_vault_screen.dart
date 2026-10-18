import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../../../core/models/backend_catalog.dart';
import '../../../../core/providers/catalog_providers.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';

class ReconVaultScreen extends ConsumerWidget {
  const ReconVaultScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final inventory = ref.watch(vaultInventoryProvider);
    return TacticalAppScaffold(
      title: 'Recon Vault',
      actions: [
        IconButton(
          tooltip: 'Refresh media inventory',
          onPressed: () => ref.invalidate(vaultInventoryProvider),
          icon: const Icon(Icons.refresh),
        ),
      ],
      child: inventory.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _VaultMessage(
          icon: Icons.cloud_off,
          title: 'Media inventory unavailable',
          detail: error.toString(),
        ),
        data: (result) => Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(
                      Icons.video_library_outlined,
                      color: TacticalColors.accent,
                    ),
                    const SizedBox(width: 12),
                    Expanded(child: Text(result.note)),
                    const SizedBox(width: 8),
                    Chip(label: Text(result.mode.toUpperCase())),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: result.items.isEmpty
                  ? const _VaultMessage(
                      icon: Icons.video_library_outlined,
                      title: 'Vault is clear',
                      detail: 'No media items were reported by the backend.',
                    )
                  : ListView.separated(
                      itemCount: result.items.length,
                      separatorBuilder: (_, _) => const SizedBox(height: 8),
                      itemBuilder: (context, index) =>
                          _VaultTile(item: result.items[index]),
                    ),
            ),
          ],
        ),
      ),
    );
  }
}

class _VaultTile extends StatelessWidget {
  const _VaultTile({required this.item});

  final VaultItem item;

  @override
  Widget build(BuildContext context) {
    final isVideo = item.mediaType == 'video';
    final details = <String>[
      item.mediaType.toUpperCase(),
      if (item.capturedAt case final capturedAt?)
        DateFormat.yMMMd().add_jm().format(capturedAt.toLocal()),
      if (item.durationSeconds case final duration?) '${duration}s',
      if (item.sizeBytes case final size?) _formatSize(size),
    ];
    return Card(
      child: ListTile(
        leading: Icon(
          isVideo ? Icons.movie_outlined : Icons.image_outlined,
          color: TacticalColors.accent,
        ),
        title: Text(item.title),
        subtitle: Text(details.join(' · ')),
        trailing: const Chip(label: Text('DEMO')),
      ),
    );
  }

  String _formatSize(int bytes) {
    if (bytes < 1024) return '$bytes B';
    final kibibytes = bytes / 1024;
    if (kibibytes < 1024) return '${kibibytes.toStringAsFixed(1)} KB';
    return '${(kibibytes / 1024).toStringAsFixed(1)} MB';
  }
}

class _VaultMessage extends StatelessWidget {
  const _VaultMessage({
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
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 460),
        child: Card(
          child: Padding(
            padding: const EdgeInsets.all(28),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(icon, color: TacticalColors.muted, size: 48),
                const SizedBox(height: 16),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleLarge,
                  textAlign: TextAlign.center,
                ),
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
      ),
    );
  }
}
