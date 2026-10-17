import 'package:flutter/material.dart';

import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';

class ReconVaultScreen extends StatelessWidget {
  const ReconVaultScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return TacticalAppScaffold(
      title: 'Recon Vault',
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 460),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(28),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(
                    Icons.video_library_outlined,
                    color: TacticalColors.accent,
                    size: 48,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Vault is clear',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Snapshots and recordings will appear here after local '
                    'media storage is connected.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: TacticalColors.muted),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
