import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/providers/backend_providers.dart';
import '../../../../core/services/backend_connection.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';
import '../../../../shared/widgets/overlays/connection_overlay.dart';

class RigSettingsScreen extends ConsumerWidget {
  const RigSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connection = ref.watch(backendConnectionProvider);
    final health = ref.watch(backendHealthProvider);
    final backendHealth = health.asData?.value;
    final savedConnection = connection.asData?.value;
    final temperature = backendHealth?.companionTemperatureC;
    final companionStatus = health.isLoading
        ? 'CHECKING'
        : backendHealth?.backendOnline == true
        ? 'ONLINE'
        : 'UNAVAILABLE';

    final items = [
      (
        title: 'Companion health',
        subtitle: temperature == null
            ? 'Temperature telemetry unavailable'
            : 'Temperature ${temperature.toStringAsFixed(1)} °C',
        icon: Icons.memory,
        status: companionStatus,
        onTap: null,
      ),
      (
        title: 'Stick calibration',
        subtitle: 'Not exposed by the current Aero Cloud API',
        icon: Icons.gamepad_outlined,
        status: 'NOT AVAILABLE',
        onTap: null,
      ),
      (
        title: 'Failsafe policy',
        subtitle: 'Not exposed by the current Aero Cloud API',
        icon: Icons.shield_outlined,
        status: 'NOT AVAILABLE',
        onTap: null,
      ),
      (
        title: 'Backend address',
        subtitle:
            savedConnection?.baseUri.host ?? 'Set the edge computer address',
        icon: Icons.dns_outlined,
        status: connection.isLoading
            ? 'LOADING'
            : savedConnection == null
            ? 'NOT CONFIGURED'
            : companionStatus,
        onTap: () => ConnectionOverlay.show(context),
      ),
    ];

    return TacticalAppScaffold(
      title: 'Rig Settings',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Companion health is read from backend diagnostics. Stick '
            'calibration and failsafe settings are not exposed by the current '
            'backend API.',
            style: TextStyle(color: TacticalColors.muted),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.separated(
              itemCount: items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 8),
              itemBuilder: (context, index) {
                final item = items[index];
                return Card(
                  child: ListTile(
                    onTap: item.onTap,
                    leading: Icon(item.icon, color: TacticalColors.accent),
                    title: Text(item.title),
                    subtitle: Text(item.subtitle),
                    trailing: Text(
                      item.status,
                      style: const TextStyle(
                        color: TacticalColors.muted,
                        fontSize: 9,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
