import 'package:flutter/material.dart';

import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';

class AiLoadoutScreen extends StatelessWidget {
  const AiLoadoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return TacticalAppScaffold(
      title: 'Edge AI Loadout',
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 560),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(
                    Icons.memory,
                    color: TacticalColors.warning,
                    size: 42,
                  ),
                  const SizedBox(height: 14),
                  Text(
                    'AI inventory unavailable',
                    style: Theme.of(context).textTheme.titleLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'The current Aero Cloud API does not expose model inventory '
                    'or inference settings. No sample model data is shown.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: TacticalColors.muted, height: 1.5),
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
