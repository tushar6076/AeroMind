import 'package:flutter/material.dart';

import '../../../core/styles/color.dart';
import '../../../core/styles/shapes.dart';

class ControlButton extends StatelessWidget {
  const ControlButton({
    required this.icon,
    required this.label,
    this.active = false,
    this.onTap,
    super.key,
  });

  final IconData icon;
  final String label;
  final bool active;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final color = active ? TacticalColors.accent : TacticalColors.muted;
    return InkWell(
      onTap: onTap,
      borderRadius: TacticalShapes.panelRadius,
      child: Container(
        constraints: const BoxConstraints(minWidth: 88),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: active ? TacticalColors.accent.withValues(alpha: 0.1) : null,
          borderRadius: TacticalShapes.panelRadius,
          border: Border.all(
            color: active ? TacticalColors.accent : TacticalColors.outline,
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: color, size: 21),
            const SizedBox(height: 7),
            Text(
              label.toUpperCase(),
              style: TextStyle(
                color: color,
                fontSize: 9,
                fontWeight: FontWeight.w800,
                letterSpacing: 0.8,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
