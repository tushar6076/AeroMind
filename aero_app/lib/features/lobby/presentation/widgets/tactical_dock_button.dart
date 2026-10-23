import 'package:flutter/material.dart';

import '../../../../core/styles/color.dart';
import '../../../../core/styles/shapes.dart';

class TacticalDockButton extends StatelessWidget {
  const TacticalDockButton({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.onTap,
    this.width = 190,
    this.compact = false,
    this.compactSize = 56,
    super.key,
  });

  final String title;
  final String subtitle;
  final IconData icon;
  final VoidCallback onTap;
  final double width;
  final bool compact;
  final double compactSize;

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return Tooltip(
        message: '$title · $subtitle',
        child: Material(
          color: TacticalColors.surface,
          borderRadius: TacticalShapes.panelRadius,
          child: InkWell(
            onTap: onTap,
            borderRadius: TacticalShapes.panelRadius,
            child: Container(
              width: compactSize,
              height: compactSize,
              decoration: BoxDecoration(
                borderRadius: TacticalShapes.panelRadius,
                border: Border.all(color: TacticalColors.outline),
              ),
              child: Icon(icon, color: TacticalColors.accent, size: 22),
            ),
          ),
        ),
      );
    }

    return Material(
      color: TacticalColors.surface,
      borderRadius: TacticalShapes.panelRadius,
      child: InkWell(
        onTap: onTap,
        borderRadius: TacticalShapes.panelRadius,
        child: Container(
          width: width,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            borderRadius: TacticalShapes.panelRadius,
            border: Border.all(color: TacticalColors.outline),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, color: TacticalColors.accent, size: 22),
              const SizedBox(width: 11),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title.toUpperCase(),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        fontSize: 11,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      subtitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: TacticalColors.muted,
                        fontSize: 10,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 10),
              const Icon(
                Icons.chevron_right,
                color: TacticalColors.muted,
                size: 17,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
