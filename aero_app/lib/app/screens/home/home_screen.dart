import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../routes/app_routes.dart';
import '../../widgets/common/app_scaffold.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      showAppBar: false,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // 1. TOP GAME HUD STATUS BAR
              _buildHudHeader(context),

              const SizedBox(height: 12),

              // 2. MAIN LAYOUT: LEFT SIDEBAR + RIGHT 3D VIEWPORT
              Expanded(
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // LEFT SIDEBAR MENU (Flexible 28% Screen Width)
                    Expanded(
                      flex: 28,
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: _buildMenuCard(
                              context,
                              title: 'COMMAND CENTER',
                              subtitle: 'Manual & Assisted Pilot',
                              icon: Icons.gamepad_outlined,
                              accentColor: const Color(0xFF00E5FF),
                              route: AppRoutes.controller,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Expanded(
                            child: _buildMenuCard(
                              context,
                              title: 'FLIGHT DETAILS',
                              subtitle: 'Live Telemetry & Metrics',
                              icon: Icons.analytics_outlined,
                              accentColor: const Color(0xFF76FF03),
                              route: AppRoutes.flightInfo,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Expanded(
                            child: _buildMenuCard(
                              context,
                              title: 'AI VISION',
                              subtitle: 'Neural Net Models',
                              icon: Icons.psychology_outlined,
                              accentColor: const Color(0xFFE040FB),
                              route: AppRoutes.aiModelsList,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Expanded(
                            child: _buildMenuCard(
                              context,
                              title: 'SYSTEM SETTINGS',
                              subtitle: 'Calibration & Config',
                              icon: Icons.tune_outlined,
                              accentColor: const Color(0xFFFFAB00),
                              route: AppRoutes.settingsOverview,
                            ),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(width: 12),

                    // RIGHT MAIN AREA: FULL-BLEED 3D DRONE STAGING VIEWPORT
                    Expanded(
                      flex: 72,
                      child: _buildDrone3DViewport(),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 10),

              // 3. BOTTOM FOOTER TELEMETRY STRIP
              _buildFooterStatus(),
            ],
          ),
        ),
      ),
    );
  }

  /// Top Status Bar styled like a sci-fi/game overlay
  Widget _buildHudHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.surface.withValues(alpha: 0.8),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.3), width: 1),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              const Icon(Icons.flight_takeoff, color: AppColors.primary, size: 22),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text(
                    'AEROMIND COMMAND',
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                      fontSize: 13,
                    ),
                  ),
                  Text(
                    'STATUS: READY TO LAUNCH',
                    style: TextStyle(
                      color: Color(0xFF00E5FF),
                      fontWeight: FontWeight.bold,
                      fontSize: 9,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ),
            ],
          ),
          Row(
            children: [
              _buildHudStatusBadge(Icons.wifi, 'LINK: 100%', Colors.greenAccent),
              const SizedBox(width: 16),
              _buildHudStatusBadge(Icons.battery_charging_full, '98%', Colors.greenAccent),
              const SizedBox(width: 16),
              _buildHudStatusBadge(Icons.gps_fixed, '12 SATS', Colors.cyanAccent),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildHudStatusBadge(IconData icon, String label, Color color) {
    return Row(
      children: [
        Icon(icon, color: color, size: 14),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 10),
        ),
      ],
    );
  }

  /// Interactive menu card for vertical sidebar layout with fixed inner constraints
  Widget _buildMenuCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color accentColor,
    required String route,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: () => Navigator.pushNamed(context, route),
        borderRadius: BorderRadius.circular(10),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: accentColor.withValues(alpha: 0.4), width: 1.5),
            gradient: LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                AppColors.surface,
                accentColor.withValues(alpha: 0.08),
              ],
            ),
            boxShadow: [
              BoxShadow(
                color: accentColor.withValues(alpha: 0.12),
                blurRadius: 8,
                spreadRadius: 1,
              )
            ],
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: accentColor.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, size: 20, color: accentColor),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min, // Fixes RenderFlex constraints
                  children: [
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.w900,
                        fontSize: 10.5,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 1),
                    Text(
                      subtitle,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        color: AppColors.textSecondary.withValues(alpha: 0.8),
                        fontSize: 8.5,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(
                Icons.arrow_forward_ios_rounded,
                size: 10,
                color: accentColor.withValues(alpha: 0.6),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// 3D Drone Display Area (Fills full right vertical & horizontal bounds)
  Widget _buildDrone3DViewport() {
    return Container(
      width: double.infinity,
      height: double.infinity,
      decoration: BoxDecoration(
        color: AppColors.surface.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primary.withValues(alpha: 0.2)),
      ),
      child: Stack(
        children: [
          // Tactical Grid Overlay Background
          Positioned.fill(
            child: CustomPaint(
              painter: TacticalGridPainter(),
            ),
          ),

          // Central Drone Model Representation
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Stack(
                  alignment: Alignment.center,
                  children: [
                    Container(
                      width: 160,
                      height: 160,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: const Color(0xFF00E5FF).withValues(alpha: 0.2),
                          width: 1.5,
                        ),
                      ),
                    ),
                    Icon(
                      Icons.flight_outlined,
                      size: 88,
                      color: AppColors.primary.withValues(alpha: 0.85),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                const Text(
                  '3D MODEL VIEWPORT',
                  style: TextStyle(
                    color: AppColors.textPrimary,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1.5,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Integrate flutter_cube or model_viewer_plus for GLB rendering',
                  style: TextStyle(
                    color: AppColors.textSecondary.withValues(alpha: 0.6),
                    fontSize: 9.5,
                  ),
                ),
              ],
            ),
          ),

          // Viewport Corner HUD Accents
          Positioned(
            top: 12,
            left: 12,
            child: Text(
              'PITCH: 0.0°  |  ROLL: 0.0°  |  YAW: 182°',
              style: TextStyle(
                color: Colors.cyanAccent.withValues(alpha: 0.7),
                fontSize: 9,
                fontFamily: 'monospace',
              ),
            ),
          ),
          Positioned(
            bottom: 12,
            right: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.black45,
                borderRadius: BorderRadius.circular(4),
                border: Border.all(color: Colors.cyanAccent.withValues(alpha: 0.3)),
              ),
              child: const Text(
                'MODEL: ESP32_AERO_V1',
                style: TextStyle(
                  color: Colors.cyanAccent,
                  fontSize: 9,
                  fontFamily: 'monospace',
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Sci-Fi Bottom Console Log Strip
  Widget _buildFooterStatus() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.4),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.white10),
      ),
      child: const Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            'SYS_MODE: UDP_ASYNC // SECURE_SOCKET: CONNECTED',
            style: TextStyle(color: Colors.white38, fontSize: 10, fontFamily: 'monospace'),
          ),
          Text(
            'BUILD v1.0.4 - AEROMIND',
            style: TextStyle(color: Colors.white38, fontSize: 10, fontFamily: 'monospace'),
          ),
        ],
      ),
    );
  }
}

/// Draws a subtle tactical grid background for the 3D viewport
class TacticalGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withValues(alpha: 0.03)
      ..strokeWidth = 1.0;

    const double step = 24.0;

    for (double x = 0; x < size.width; x += step) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += step) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}