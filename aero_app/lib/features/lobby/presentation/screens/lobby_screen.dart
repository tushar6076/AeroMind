import 'package:flutter/material.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/buttons/tactical_button.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';
import '../../../../shared/widgets/overlays/connection_overlay.dart';
import '../widgets/tactical_dock_button.dart';
import '../widgets/top_status_dock.dart';

class LobbyScreen extends StatelessWidget {
  const LobbyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return TacticalAppScaffold(
      title: 'Tactical Lobby',
      showBackButton: false,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final isWide = constraints.maxWidth >= 820;
          return SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    const TopStatusDock(),
                    OutlinedButton.icon(
                      onPressed: () => ConnectionOverlay.show(context),
                      icon: const Icon(Icons.settings_ethernet, size: 16),
                      label: const Text('LINK DETAILS'),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                if (isWide)
                  SizedBox(
                    height: 390,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _NavigationDock(
                          firstTitle: 'Flight modes',
                          firstSubtitle: 'Operational profile',
                          firstIcon: Icons.explore,
                          firstTap: () => _push(context, AppRoutes.flightModes),
                          secondTitle: 'Edge AI',
                          secondSubtitle: 'Model loadout',
                          secondIcon: Icons.memory,
                          secondTap: () => _push(context, AppRoutes.edgeAi),
                        ),
                        const SizedBox(width: 16),
                        const Expanded(child: _AircraftPanel()),
                        const SizedBox(width: 16),
                        _NavigationDock.media(
                          firstTap: () => _push(context, AppRoutes.vault),
                          secondTap: () => _push(context, AppRoutes.settings),
                        ),
                      ],
                    ),
                  )
                else ...[
                  const SizedBox(height: 240, child: _AircraftPanel()),
                  const SizedBox(height: 14),
                  Wrap(
                    spacing: 10,
                    runSpacing: 10,
                    children: [
                      TacticalDockButton(
                        title: 'Flight modes',
                        subtitle: 'Operational profile',
                        icon: Icons.explore,
                        onTap: () => _push(context, AppRoutes.flightModes),
                      ),
                      TacticalDockButton(
                        title: 'Edge AI',
                        subtitle: 'Model loadout',
                        icon: Icons.memory,
                        onTap: () => _push(context, AppRoutes.edgeAi),
                      ),
                      TacticalDockButton(
                        title: 'Recon vault',
                        subtitle: 'Local media',
                        icon: Icons.video_library_outlined,
                        onTap: () => _push(context, AppRoutes.vault),
                      ),
                      TacticalDockButton(
                        title: 'Rig settings',
                        subtitle: 'Hardware & controls',
                        icon: Icons.tune,
                        onTap: () => _push(context, AppRoutes.settings),
                      ),
                    ],
                  ),
                ],
                const SizedBox(height: 18),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(18),
                    child: Row(
                      children: [
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'FLIGHT OPERATIONS',
                                style: TextStyle(
                                  color: TacticalColors.accent,
                                  fontSize: 10,
                                  fontWeight: FontWeight.w900,
                                  letterSpacing: 1.5,
                                ),
                              ),
                              SizedBox(height: 7),
                              Text(
                                'Run pre-flight checks before entering the HUD.',
                                style: TextStyle(color: TacticalColors.muted),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(width: 12),
                        TacticalButton(
                          label: 'DEPLOY',
                          icon: Icons.rocket_launch,
                          onPressed: () =>
                              _push(context, AppRoutes.flightModes),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  static void _push(BuildContext context, String route) {
    Navigator.of(context).pushNamed(route);
  }
}

class _NavigationDock extends StatelessWidget {
  const _NavigationDock({
    required this.firstTitle,
    required this.firstSubtitle,
    required this.firstIcon,
    required this.firstTap,
    required this.secondTitle,
    required this.secondSubtitle,
    required this.secondIcon,
    required this.secondTap,
  });

  const _NavigationDock.media({required this.firstTap, required this.secondTap})
    : firstTitle = 'Recon vault',
      firstSubtitle = 'Local media',
      firstIcon = Icons.video_library_outlined,
      secondTitle = 'Rig settings',
      secondSubtitle = 'Hardware & controls',
      secondIcon = Icons.tune;

  final String firstTitle;
  final String firstSubtitle;
  final IconData firstIcon;
  final VoidCallback firstTap;
  final String secondTitle;
  final String secondSubtitle;
  final IconData secondIcon;
  final VoidCallback secondTap;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 190,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TacticalDockButton(
            title: firstTitle,
            subtitle: firstSubtitle,
            icon: firstIcon,
            onTap: firstTap,
          ),
          const SizedBox(height: 12),
          TacticalDockButton(
            title: secondTitle,
            subtitle: secondSubtitle,
            icon: secondIcon,
            onTap: secondTap,
          ),
        ],
      ),
    );
  }
}

class _AircraftPanel extends StatelessWidget {
  const _AircraftPanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: TacticalColors.surface.withValues(alpha: 0.65),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: TacticalColors.outline),
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          const Positioned.fill(child: CustomPaint(painter: _GridPainter())),
          Container(
            width: 220,
            height: 220,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: TacticalColors.accent.withValues(alpha: 0.25),
              ),
            ),
          ),
          const Icon(
            Icons.airplanemode_active,
            size: 114,
            color: TacticalColors.accent,
          ),
          const Positioned(
            left: 18,
            top: 16,
            child: _PanelTag(label: 'AIRFRAME', value: 'NOT LINKED'),
          ),
          const Positioned(
            right: 18,
            bottom: 16,
            child: _PanelTag(label: 'ACTIVE PROFILE', value: 'NOT SELECTED'),
          ),
        ],
      ),
    );
  }
}

class _PanelTag extends StatelessWidget {
  const _PanelTag({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: TacticalColors.muted,
            fontSize: 9,
            letterSpacing: 1.1,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: TacticalColors.warning,
            fontSize: 10,
            fontWeight: FontWeight.w900,
          ),
        ),
      ],
    );
  }
}

class _GridPainter extends CustomPainter {
  const _GridPainter();

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = TacticalColors.outline.withValues(alpha: 0.35)
      ..strokeWidth = 1;
    for (var x = 0.0; x < size.width; x += 28) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (var y = 0.0; y < size.height; y += 28) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
