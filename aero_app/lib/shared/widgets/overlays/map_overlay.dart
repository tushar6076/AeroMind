import 'package:flutter/material.dart';

import '../../../core/models/backend_status.dart';
import '../../../core/styles/color.dart';

class MapOverlay extends StatelessWidget {
  const MapOverlay({this.telemetry, super.key});

  final TelemetrySnapshot? telemetry;

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 1,
      child: Container(
        constraints: const BoxConstraints(maxWidth: 220, maxHeight: 220),
        decoration: BoxDecoration(
          color: TacticalColors.surface,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: TacticalColors.outline),
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            const Positioned.fill(child: CustomPaint(painter: _RadarPainter())),
            Icon(
              (telemetry?.gpsSatellites ?? 0) >= 6
                  ? Icons.gps_fixed
                  : Icons.gps_not_fixed,
              color: (telemetry?.gpsSatellites ?? 0) >= 6
                  ? TacticalColors.accent
                  : TacticalColors.warning,
            ),
            const Positioned(
              left: 12,
              top: 10,
              child: Text(
                'GPS RADAR',
                style: TextStyle(
                  color: TacticalColors.muted,
                  fontSize: 9,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1,
                ),
              ),
            ),
            Positioned(
              bottom: 10,
              child: Text(
                (telemetry?.gpsSatellites ?? 0) < 6
                    ? 'POSITION UNAVAILABLE'
                    : '${telemetry!.gpsSatellites} SATELLITES',
                style: TextStyle(
                  color: (telemetry?.gpsSatellites ?? 0) < 6
                      ? TacticalColors.warning
                      : TacticalColors.accent,
                  fontSize: 8,
                  fontWeight: FontWeight.w800,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _RadarPainter extends CustomPainter {
  const _RadarPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final radius = size.shortestSide * 0.36;
    final paint = Paint()
      ..color = TacticalColors.accent.withValues(alpha: 0.18)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1;
    for (var factor = 0.33; factor <= 1; factor += 0.33) {
      canvas.drawCircle(center, radius * factor, paint);
    }
    canvas.drawLine(
      Offset(center.dx - radius, center.dy),
      Offset(center.dx + radius, center.dy),
      paint,
    );
    canvas.drawLine(
      Offset(center.dx, center.dy - radius),
      Offset(center.dx, center.dy + radius),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
