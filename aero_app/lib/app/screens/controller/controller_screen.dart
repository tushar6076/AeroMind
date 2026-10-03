import 'package:flutter/material.dart';

import '../../core/constants/app_colors.dart';
import '../../widgets/buttons/control_button.dart';
import '../../widgets/common/app_scaffold.dart';
import '../../widgets/joysticks/joystick_left.dart';
import '../../widgets/joysticks/joystick_right.dart';
import '../../widgets/overlays/camera_overlay.dart';
import '../../widgets/overlays/map_overlay.dart';

class ControllerScreen extends StatefulWidget {
  const ControllerScreen({super.key});

  @override
  State<ControllerScreen> createState() => _ControllerScreenState();
}

class _ControllerScreenState extends State<ControllerScreen> {
  bool _isArmed = true;
  bool _isVideoActive = false;

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Command Center HUD',
      body: Stack(
        children: [
          // 1. Camera / Video Feed Viewport Base
          Positioned.fill(
            child: Container(
              color: AppColors.background,
              child: _isVideoActive
                  ? const CameraOverlay()
                  : Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: AppColors.surface.withValues(alpha: 0.6),
                              border: Border.all(
                                color: AppColors.textMuted.withValues(alpha: 0.2),
                              ),
                            ),
                            child: const Icon(
                              Icons.videocam_off_outlined,
                              size: 48,
                              color: AppColors.textMuted,
                            ),
                          ),
                          const SizedBox(height: 12),
                          const Text(
                            'VIDEO STREAM OFFLINE',
                            style: TextStyle(
                              color: AppColors.textMuted,
                              fontSize: 13,
                              letterSpacing: 1.2,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 12),
                          OutlinedButton.icon(
                            style: OutlinedButton.styleFrom(
                              foregroundColor: AppColors.primary,
                              side: const BorderSide(color: AppColors.primary),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(20),
                              ),
                            ),
                            icon: const Icon(Icons.refresh, size: 16),
                            label: const Text('Reconnect Camera'),
                            onPressed: () {
                              setState(() {
                                _isVideoActive = true;
                              });
                            },
                          ),
                        ],
                      ),
                    ),
            ),
          ),

          // 2. HUD Telemetry Bar (Top)
          Positioned(
            top: 12,
            left: 12,
            right: 180, // Leave room for top-right Map Overlay
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.surface.withValues(alpha: 0.85),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.primary.withValues(alpha: 0.3)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withValues(alpha: 0.4),
                    blurRadius: 8,
                  ),
                ],
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _StatusChip(
                    label: 'SYSTEM',
                    value: _isArmed ? 'ARMED' : 'DISARMED',
                    color: _isArmed ? AppColors.success : Colors.redAccent,
                  ),
                  const _StatusChip(
                    label: 'BATTERY',
                    value: '88%',
                    color: AppColors.primary,
                  ),
                  const _StatusChip(
                    label: 'SIGNAL',
                    value: '-65 dBm',
                    color: AppColors.warning,
                  ),
                  const _StatusChip(
                    label: 'ALTITUDE',
                    value: '14.2 m',
                    color: AppColors.textPrimary,
                  ),
                ],
              ),
            ),
          ),

          // 3. Mini-Map Tactical Overlay (Top-Right Game Style)
          const Positioned(
            top: 12,
            right: 12,
            width: 150,
            height: 150,
            child: MapOverlay(),
          ),

          // 4. Game Controller Layout (Bottom Joysticks & Flight Controls)
          Positioned(
            bottom: 16,
            left: 16,
            right: 16,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                // Left Throttle & Yaw Joystick
                const SizedBox(
                  width: 140,
                  height: 140,
                  child: JoystickLeft(),
                ),

                // Center Command Action Bar
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.surface.withValues(alpha: 0.85),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: AppColors.textSecondary.withValues(alpha: 0.2)),
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      ControlButton(
                        label: _isArmed ? 'DISARM' : 'ARM',
                        icon: _isArmed ? Icons.power_settings_new : Icons.verified_user,
                        backgroundColor: _isArmed ? Colors.redAccent : AppColors.success,
                        onPressed: () {
                          setState(() {
                            _isArmed = !_isArmed;
                          });
                        },
                      ),
                      const SizedBox(height: 8),
                      ControlButton(
                        label: 'TAKEOFF',
                        icon: Icons.flight_takeoff,
                        backgroundColor: AppColors.primary,
                        onPressed: () {
                          if (_isArmed) {
                            // Takeoff execution logic
                          }
                        },
                      ),
                      const SizedBox(height: 8),
                      ControlButton(
                        label: 'AUTO RTL',
                        icon: Icons.home,
                        backgroundColor: AppColors.warning,
                        onPressed: () {
                          if (_isArmed) {
                            // Return To Launch execution logic
                          }
                        },
                      ),
                    ],
                  ),
                ),

                // Right Pitch & Roll Joystick
                const SizedBox(
                  width: 140,
                  height: 140,
                  child: JoystickRight(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatusChip extends StatelessWidget {
  final String label;
  final String value;
  final Color color;

  const _StatusChip({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: AppColors.textSecondary,
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 13,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }
}