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
          final isShort = constraints.maxHeight < 340;
          return Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Wrap(
                spacing: 10,
                runSpacing: 8,
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
              SizedBox(height: isShort ? 10 : 16),
              Expanded(
                child: LayoutBuilder(
                  builder: (context, mainConstraints) {
                    final compactDocks =
                        constraints.maxWidth < 680 ||
                        mainConstraints.maxHeight < 132;
                    final gap = compactDocks ? 8.0 : 12.0;
                    final dockWidth = compactDocks
                        ? 56.0
                        : ((constraints.maxWidth - 324) / 2)
                              .clamp(160.0, 190.0)
                              .toDouble();
                    final buttonSize = compactDocks
                        ? ((mainConstraints.maxHeight - gap) / 2)
                              .clamp(36.0, 56.0)
                              .toDouble()
                        : 56.0;

                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        _NavigationDock(
                          width: dockWidth,
                          compact: compactDocks,
                          buttonSize: buttonSize,
                          firstTitle: 'Flight modes',
                          firstSubtitle: 'Operational profile',
                          firstIcon: Icons.explore,
                          firstTap: () => _push(context, AppRoutes.flightModes),
                          secondTitle: 'Edge AI',
                          secondSubtitle: 'Model loadout',
                          secondIcon: Icons.memory,
                          secondTap: () => _push(context, AppRoutes.edgeAi),
                        ),
                        SizedBox(width: gap),
                        const Expanded(child: _AircraftPanel()),
                        SizedBox(width: gap),
                        _NavigationDock.media(
                          width: dockWidth,
                          compact: compactDocks,
                          buttonSize: buttonSize,
                          firstTap: () => _push(context, AppRoutes.vault),
                          secondTap: () => _push(context, AppRoutes.settings),
                        ),
                      ],
                    );
                  },
                ),
              ),
              SizedBox(height: isShort ? 10 : 16),
              _FlightOperationsPanel(
                compact: isShort,
                onDeploy: () => _push(context, AppRoutes.flightModes),
              ),
            ],
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
    required this.width,
    required this.compact,
    required this.buttonSize,
    required this.firstTitle,
    required this.firstSubtitle,
    required this.firstIcon,
    required this.firstTap,
    required this.secondTitle,
    required this.secondSubtitle,
    required this.secondIcon,
    required this.secondTap,
  });

  const _NavigationDock.media({
    required this.width,
    required this.compact,
    required this.buttonSize,
    required this.firstTap,
    required this.secondTap,
  }) : firstTitle = 'Recon vault',
       firstSubtitle = 'Local media',
       firstIcon = Icons.video_library_outlined,
       secondTitle = 'Rig settings',
       secondSubtitle = 'Hardware & controls',
       secondIcon = Icons.tune;

  final double width;
  final bool compact;
  final double buttonSize;
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
      width: width,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          TacticalDockButton(
            title: firstTitle,
            subtitle: firstSubtitle,
            icon: firstIcon,
            onTap: firstTap,
            width: width,
            compact: compact,
            compactSize: buttonSize,
          ),
          SizedBox(height: compact ? 8 : 12),
          TacticalDockButton(
            title: secondTitle,
            subtitle: secondSubtitle,
            icon: secondIcon,
            onTap: secondTap,
            width: width,
            compact: compact,
            compactSize: buttonSize,
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
          LayoutBuilder(
            builder: (context, constraints) {
              final extent = constraints.biggest.shortestSide;
              return Container(
                width: extent * 0.68,
                height: extent * 0.68,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: TacticalColors.accent.withValues(alpha: 0.25),
                  ),
                ),
              );
            },
          ),
          LayoutBuilder(
            builder: (context, constraints) {
              final planeSize = constraints.biggest.shortestSide * 0.4;
              return Icon(
                Icons.airplanemode_active,
                size: planeSize,
                color: TacticalColors.accent,
              );
            },
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

class _FlightOperationsPanel extends StatelessWidget {
  const _FlightOperationsPanel({required this.compact, required this.onDeploy});

  final bool compact;
  final VoidCallback onDeploy;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: EdgeInsets.symmetric(
          horizontal: compact ? 12 : 18,
          vertical: compact ? 8 : 14,
        ),
        child: Row(
          children: [
            const Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
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
                  SizedBox(height: 5),
                  Text(
                    'Run pre-flight checks before entering the HUD.',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(color: TacticalColors.muted),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            TacticalButton(
              label: 'DEPLOY',
              icon: Icons.rocket_launch,
              onPressed: onDeploy,
            ),
          ],
        ),
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
