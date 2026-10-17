import 'package:flutter/material.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/buttons/tactical_button.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';

class PostFlightScreen extends StatelessWidget {
  const PostFlightScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return TacticalAppScaffold(
      title: 'Mission Debrief',
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 640),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(
                    Icons.summarize_outlined,
                    color: TacticalColors.accent,
                    size: 46,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'No mission data yet',
                    style: Theme.of(context).textTheme.headlineSmall
                        ?.copyWith(fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Flight metrics and detections will be shown here from the '
                    'completed backend session.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: TacticalColors.muted),
                  ),
                  const SizedBox(height: 20),
                  const Wrap(
                    alignment: WrapAlignment.center,
                    spacing: 10,
                    runSpacing: 10,
                    children: [
                      _Metric(label: 'DURATION', value: '--'),
                      _Metric(label: 'DISTANCE', value: '--'),
                      _Metric(label: 'PEAK SPEED', value: '--'),
                      _Metric(label: 'EVENTS', value: '--'),
                    ],
                  ),
                  const SizedBox(height: 22),
                  TacticalButton(
                    label: 'RETURN TO LOBBY',
                    icon: Icons.home_outlined,
                    onPressed: () => Navigator.of(context)
                        .pushNamedAndRemoveUntil(AppRoutes.lobby, (_) => false),
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

class _Metric extends StatelessWidget {
  const _Metric({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 116,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: TacticalColors.elevated,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 5),
          Text(
            label,
            style: const TextStyle(
              color: TacticalColors.muted,
              fontSize: 8,
              letterSpacing: 0.8,
            ),
          ),
        ],
      ),
    );
  }
}
