import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/models/backend_status.dart';
import '../../../../core/network/http_client.dart';
import '../../../../core/providers/backend_providers.dart';
import '../../../../core/router/app_router.dart';
import '../../../../core/styles/shapes.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/buttons/tactical_button.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';

class PreFlightScreen extends ConsumerWidget {
  const PreFlightScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final health = ref.watch(backendHealthProvider);
    final isReady = health.asData?.value.readyForFlight == true;
    return TacticalAppScaffold(
      title: 'Pre-flight Diagnostics',
      actions: [
        IconButton(
          tooltip: 'Refresh diagnostics',
          onPressed: () => ref.read(backendHealthProvider.notifier).refresh(),
          icon: const Icon(Icons.refresh),
        ),
      ],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Icon(
                    isReady ? Icons.check_circle : Icons.warning_amber,
                    color: isReady
                        ? TacticalColors.accent
                        : TacticalColors.warning,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      isReady
                          ? 'All configured checks passed. Start a session to '
                                'open the HUD; arming remains a separate action.'
                          : 'Flight readiness is not verified. Arming and '
                                'control stay locked until backend checks pass.',
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: health.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => _StatusMessage(
                icon: Icons.cloud_off,
                title: 'Aero Cloud unavailable',
                detail: error.toString(),
              ),
              data: (result) => ListView.separated(
                itemCount: result.checks.length,
                separatorBuilder: (_, _) => const SizedBox(height: 8),
                itemBuilder: (context, index) {
                  final check = result.checks[index];
                  return _ReadinessTile(check: check);
                },
              ),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Text(
                  isReady
                      ? 'READINESS CONFIRMED · ARMING IS A SEPARATE STEP'
                      : 'ARMING DISABLED · CHECKS NOT PASSED',
                  style: TextStyle(
                    color: isReady
                        ? TacticalColors.accent
                        : TacticalColors.warning,
                    fontSize: 9,
                    fontWeight: FontWeight.w900,
                    letterSpacing: 0.8,
                  ),
                ),
              ),
              if (isReady) ...[
                TacticalButton(
                  label: 'START SESSION',
                  icon: Icons.flight_takeoff,
                  onPressed: () => _startSession(context, ref),
                ),
                const SizedBox(width: 8),
              ],
              TacticalButton(
                label: 'PREVIEW HUD',
                icon: Icons.visibility_outlined,
                filled: false,
                onPressed: () =>
                    Navigator.of(context)
                        .pushNamed(AppRoutes.liveFlight, arguments: true),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _startSession(BuildContext context, WidgetRef ref) async {
    try {
      await ref.read(aeroCloudClientProvider).startFlightSession();
      ref.invalidate(flightStatusProvider);
      if (context.mounted) {
        await Navigator.of(context).pushNamed(AppRoutes.liveFlight);
      }
    } on Exception catch (error) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not start flight session: $error')),
      );
    }
  }
}

class _ReadinessTile extends StatelessWidget {
  const _ReadinessTile({required this.check});

  final ReadinessCheck check;

  @override
  Widget build(BuildContext context) {
    final color = check.ready ? TacticalColors.accent : TacticalColors.warning;
    return Card(
      child: ListTile(
        leading: Icon(
          check.ready ? Icons.check_circle_outline : Icons.pending_outlined,
          color: color,
        ),
        title: Text(check.name),
        subtitle: Text(check.detail),
        trailing: Text(
          check.ready ? 'READY' : 'CHECK',
          style: TextStyle(
            color: color,
            fontSize: 9,
            fontWeight: FontWeight.w900,
            letterSpacing: 0.8,
          ),
        ),
      ),
    );
  }
}

class _StatusMessage extends StatelessWidget {
  const _StatusMessage({
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
      child: Container(
        constraints: const BoxConstraints(maxWidth: 520),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          border: Border.all(color: TacticalColors.outline),
          borderRadius: TacticalShapes.panelRadius,
          color: TacticalColors.surface,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 38, color: TacticalColors.warning),
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
    );
  }
}
