import 'package:flutter/material.dart';

class JoystickRight extends StatelessWidget {
  const JoystickRight({
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
    return _RightJoystick(
      position: position,
      enabled: enabled,
      onChanged: onChanged,
    );
  }
}

class _RightJoystick extends StatelessWidget {
  const _RightJoystick({
    required this.position,
    required this.enabled,
    required this.onChanged,
  });

  final Offset position;
  final bool enabled;
  final ValueChanged<Offset> onChanged;

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
                  ? (details) {
                      const radius = 52.0;
                      onChanged(
                        Offset(
                          ((details.localPosition.dx - radius) /
                                  (radius * 0.72))
                              .clamp(-1.0, 1.0),
                          ((details.localPosition.dy - radius) /
                                  (radius * 0.72))
                              .clamp(-1.0, 1.0),
                        ),
                      );
                    }
                  : null,
              onPanEnd: enabled ? (_) => onChanged(Offset.zero) : null,
              child: CustomPaint(
                painter: _RightJoystickPainter(
                  position: position,
                  enabled: enabled,
                ),
              ),
            ),
          ),
          const SizedBox(height: 5),
          const Text(
            'PITCH / ROLL',
            style: TextStyle(
              color: Color(0xFF8FA2AA),
              fontSize: 8,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.8,
            ),
          ),
        ],
      ),
    );
  }
}

class _RightJoystickPainter extends CustomPainter {
  const _RightJoystickPainter({required this.position, required this.enabled});

  final Offset position;
  final bool enabled;

  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final radius = size.shortestSide / 2 - 4;
    final ring = Paint()
      ..color = const Color(0xFF2A3B45)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    final crosshair = Paint()
      ..color = const Color(0xFF8FA2AA).withValues(alpha: 0.55)
      ..strokeWidth = 1;
    final knob = Paint()
      ..color = enabled ? const Color(0xFF16242D) : const Color(0xFF101B23);
    final knobBorder = Paint()
      ..color = enabled ? const Color(0xFF54F0C0) : const Color(0xFF8FA2AA)
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
    final knobPosition = Offset(
      center.dx + position.dx * radius * 0.58,
      center.dy + position.dy * radius * 0.58,
    );
    canvas.drawCircle(knobPosition, radius * 0.28, knob);
    canvas.drawCircle(knobPosition, radius * 0.28, knobBorder);
  }

  @override
  bool shouldRepaint(covariant _RightJoystickPainter oldDelegate) =>
      oldDelegate.position != position || oldDelegate.enabled != enabled;
}
