import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/models/backend_status.dart';
import '../../../../core/providers/backend_providers.dart';
import '../../../../core/services/backend_connection.dart';
import '../../../../core/styles/color.dart';

class TopStatusDock extends ConsumerWidget {
  const TopStatusDock({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final connection = ref.watch(backendConnectionProvider);
    final health = ref.watch(backendHealthProvider);
    final data = health.asData?.value;
    final backendValue = health.isLoading
        ? 'CHECKING'
        : data?.backendOnline == true
        ? 'ONLINE'
        : connection.hasError
        ? 'CONFIG ERROR'
        : connection.asData?.value == null
        ? 'NOT CONFIGURED'
        : 'OFFLINE';
    final backendColor = data?.backendOnline == true
        ? TacticalColors.accent
        : connection.asData?.value == null
        ? TacticalColors.muted
        : TacticalColors.warning;

    return Wrap(
      spacing: 8,
      runSpacing: 8,
      alignment: WrapAlignment.end,
      children: [
        _StatusPill(
          label: 'BACKEND',
          value: backendValue,
          color: backendColor,
          icon: data?.backendOnline == true
              ? Icons.cloud_done
              : Icons.cloud_off,
        ),
        _StatusPill(
          label: 'AIR LINK',
          value: _linkValue(data),
          color: data?.elrsConnected == true
              ? TacticalColors.accent
              : TacticalColors.warning,
          icon: data?.elrsConnected == true ? Icons.sensors : Icons.sensors_off,
        ),
        _StatusPill(
          label: 'VIDEO',
          value: _videoValue(data),
          color: data?.videoInputAvailable == true
              ? TacticalColors.accent
              : TacticalColors.muted,
          icon: data?.videoInputAvailable == true
              ? Icons.videocam
              : Icons.videocam_off,
        ),
      ],
    );
  }

  static String _linkValue(BackendHealth? health) {
    if (health == null) return 'UNKNOWN';
    if (!health.elrsConfigured) return 'NOT CONFIGURED';
    if (!health.elrsConnected) return 'NO SIGNAL';
    return health.elrsLinkQuality == null
        ? 'WAITING'
        : 'LQ ${health.elrsLinkQuality}%';
  }

  static String _videoValue(BackendHealth? health) {
    if (health == null) return 'UNKNOWN';
    if (!health.videoInputConfigured) return 'NOT CONFIGURED';
    if (!health.videoInputAvailable) return 'NO DEVICE';
    return health.videoStreaming ? 'STREAMING' : 'READY';
  }
}

class _StatusPill extends StatelessWidget {
  const _StatusPill({
    required this.label,
    required this.value,
    required this.color,
    required this.icon,
  });

  final String label;
  final String value;
  final Color color;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 164,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: TacticalColors.surface,
          border: Border.all(color: TacticalColors.outline),
          borderRadius: BorderRadius.circular(9),
        ),
        child: Row(
          children: [
            Icon(icon, color: color, size: 15),
            const SizedBox(width: 7),
            Text(
              '$label  ',
              maxLines: 1,
              style: const TextStyle(
                color: TacticalColors.muted,
                fontSize: 9,
                fontWeight: FontWeight.w700,
              ),
            ),
            Expanded(
              child: Text(
                value,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  color: color,
                  fontSize: 9,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 0.6,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
