import 'package:flutter/material.dart';

import '../../../core/styles/color.dart';

class JoystickLeft extends StatelessWidget {
  const JoystickLeft({
    required this.position,
    required this.enabled,
    required this.onChanged,
    super.key,
  });

  final Offset position;
  final bool enabled;
  final ValueChanged<Offset> onChanged;

  @override
  Widget build(BuildContext context) {
    return _Joystick(
      position: position,
      enabled: enabled,
      label: 'THROTTLE HOLD / YAW',
      onChanged: onChanged,
      onReleased: () => onChanged(Offset(0, position.dy)),
      throttleAxis: true,
    );
  }
}

class _Joystick extends StatelessWidget {
  const _Joystick({
    required this.position,
    required this.enabled,
    required this.label,
    required this.onChanged,
    required this.onReleased,
    this.throttleAxis = false,
  });

  final Offset position;
  final bool enabled;
  final String label;
  final ValueChanged<Offset> onChanged;
  final VoidCallback onReleased;
  final bool throttleAxis;

  @override
  Widget build(BuildContext context) {
    const size = 112.0;
    return Opacity(
      opacity: enabled ? 1 : 0.48,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(
            width: size,
            height: size,
            child: GestureDetector(
              onPanUpdate: enabled
                  ? (details) => onChanged(_positionFrom(details.localPosition))
                  : null,
              onPanEnd: enabled ? (_) => onReleased() : null,
              child: CustomPaint(
                painter: _JoystickPainter(
                  position: position,
                  throttleAxis: throttleAxis,
                  enabled: enabled,
                ),
              ),
            ),
          ),
          const SizedBox(height: 5),
          Text(
            label,
            style: const TextStyle(
              color: TacticalColors.muted,
              fontSize: 8,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.8,
            ),
          ),
        ],
      ),
    );
  }

  Offset _positionFrom(Offset point) {
    const radius = 52.0;
    final x = ((point.dx - radius) / (radius * 0.72)).clamp(-1.0, 1.0);
    final vertical = ((point.dy - radius) / (radius * 0.72)).clamp(-1.0, 1.0);
    return throttleAxis ? Offset(x, (1 - vertical) / 2) : Offset(x, vertical);
  }
}

class _JoystickPainter extends CustomPainter {
  const _JoystickPainter({
    required this.position,
    required this.throttleAxis,
    required this.enabled,
  });

  final Offset position;
  final bool throttleAxis;
  final bool enabled;

  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final radius = size.shortestSide / 2 - 4;
    final ring = Paint()
      ..color = TacticalColors.outline
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    final crosshair = Paint()
      ..color = TacticalColors.muted.withValues(alpha: 0.55)
      ..strokeWidth = 1;
    final knob = Paint()
      ..color = enabled ? TacticalColors.elevated : TacticalColors.surface;
    final knobBorder = Paint()
      ..color = enabled ? TacticalColors.accent : TacticalColors.muted
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawCircle(center, radius, ring);
    canvas.drawLine(
      Offset(center.dx - radius * 0.65, center.dy),
      Offset(center.dx + radius * 0.65, center.dy),
      crosshair,
    );
    canvas.drawLine(
      Offset(center.dx, center.dy - radius * 0.65),
      Offset(center.dx, center.dy + radius * 0.65),
      crosshair,
    );
    final vertical = throttleAxis ? (0.5 - position.dy) * 2 : position.dy;
    final knobPosition = Offset(
      center.dx + position.dx * radius * 0.58,
      center.dy + vertical * radius * 0.58,
    );
    canvas.drawCircle(knobPosition, radius * 0.28, knob);
    canvas.drawCircle(knobPosition, radius * 0.28, knobBorder);
  }

  @override
  bool shouldRepaint(covariant _JoystickPainter oldDelegate) =>
      oldDelegate.position != position ||
      oldDelegate.enabled != enabled ||
      oldDelegate.throttleAxis != throttleAxis;
}
