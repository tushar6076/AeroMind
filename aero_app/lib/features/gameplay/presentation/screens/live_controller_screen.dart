import 'package:flutter/material.dart';

import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/buttons/tactical_button.dart';
import '../../../../shared/widgets/joysticks/joystick_left.dart';
import '../../../../shared/widgets/joysticks/joystick_right.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';
import '../../../../shared/widgets/overlays/map_overlay.dart';

class LiveControllerScreen extends StatelessWidget {
  const LiveControllerScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return TacticalAppScaffold(
      title: 'HUD Preview',
      actions: const [
        Chip(
          avatar: Icon(Icons.visibility_outlined, size: 15),
          label: Text('PREVIEW ONLY'),
        ),
      ],
      child: LayoutBuilder(
        builder: (context, constraints) {
          final compact = constraints.maxWidth < 760;
          return Column(
            children: [
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Expanded(child: _VideoPanel()),
                    const SizedBox(width: 12),
                    if (!compact) const MapOverlay(),
                  ],
                ),
              ),
              if (compact) ...[
                const SizedBox(height: 8),
                const SizedBox(height: 150, child: MapOverlay()),
              ],
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  JoystickLeft(
                    position: Offset.zero,
                    enabled: false,
                    onChanged: (_) {},
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Text(
                        'CONTROL LINK OFFLINE',
                        style: TextStyle(
                          color: TacticalColors.warning,
                          fontSize: 9,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1,
                        ),
                      ),
                      const SizedBox(height: 8),
                      TacticalButton(
                        label: 'CLOSE PREVIEW',
                        icon: Icons.close,
                        filled: false,
                        onPressed: () => Navigator.of(context).maybePop(),
                      ),
                    ],
                  ),
                  JoystickRight(
                    position: Offset.zero,
                    enabled: false,
                    onChanged: (_) {},
                  ),
                ],
              ),
            ],
          );
        },
      ),
    );
  }
}

class _VideoPanel extends StatelessWidget {
  const _VideoPanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF05090C),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: TacticalColors.outline),
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          const Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.videocam_off_outlined,
                color: TacticalColors.muted,
                size: 38,
              ),
              SizedBox(height: 12),
              Text(
                'WAITING FOR WEBRTC VIDEO',
                style: TextStyle(
                  color: TacticalColors.text,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.2,
                  fontSize: 11,
                ),
              ),
              SizedBox(height: 5),
              Text(
                '5.8 GHz receiver → backend ingest → app stream',
                style: TextStyle(color: TacticalColors.muted, fontSize: 10),
              ),
            ],
          ),
          const Positioned(
            left: 14,
            top: 12,
            child: _HudReadout(label: 'ALT', value: '--'),
          ),
          const Positioned(
            left: 78,
            top: 12,
            child: _HudReadout(label: 'SPD', value: '--'),
          ),
          const Positioned(
            right: 14,
            top: 12,
            child: _HudReadout(label: 'LINK', value: 'OFFLINE'),
          ),
          const Positioned(
            right: 14,
            bottom: 12,
            child: _HudReadout(label: 'DETECTIONS', value: '--'),
          ),
        ],
      ),
    );
  }
}

class _HudReadout extends StatelessWidget {
  const _HudReadout({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: TacticalColors.muted,
            fontSize: 8,
            letterSpacing: 1,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            color: TacticalColors.text,
            fontSize: 10,
            fontWeight: FontWeight.w900,
          ),
        ),
      ],
    );
  }
}
