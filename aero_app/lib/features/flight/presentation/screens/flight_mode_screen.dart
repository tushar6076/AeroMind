import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/router/app_router.dart';
import '../../../../core/network/http_client.dart';
import '../../../../core/services/backend_connection.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/buttons/tactical_button.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';

class FlightModeScreen extends ConsumerStatefulWidget {
  const FlightModeScreen({super.key});

  @override
  ConsumerState<FlightModeScreen> createState() => _FlightModeScreenState();
}

class _FlightModeScreenState extends ConsumerState<FlightModeScreen> {
  int _selected = 0;

  static const _modes = [
    (
      'position_hold',
      'Position Hold',
      'Stabilized position mode',
      Icons.my_location,
    ),
    (
      'waypoint_patrol',
      'Waypoint Patrol',
      'Backend-planned route',
      Icons.route,
    ),
    (
      'orbit',
      'Orbit',
      'Circular path around a point',
      Icons.radio_button_unchecked,
    ),
    ('acro', 'Acro', 'Rate-based manual profile', Icons.sports_motorsports),
  ];

  @override
  Widget build(BuildContext context) {
    return TacticalAppScaffold(
      title: 'Flight Mode Hub',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'Choose an operational profile. The selection is a local UI choice '
            'until an Aero Cloud session is connected.',
            style: TextStyle(color: TacticalColors.muted),
          ),
          const SizedBox(height: 16),
          Expanded(
            child: GridView.builder(
              itemCount: _modes.length,
              gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
                maxCrossAxisExtent: 290,
                mainAxisExtent: 150,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
              ),
              itemBuilder: (context, index) {
                final mode = _modes[index];
                final selected = _selected == index;
                return Card(
                  clipBehavior: Clip.antiAlias,
                  child: InkWell(
                    onTap: () => setState(() => _selected = index),
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: selected
                              ? TacticalColors.accent
                              : Colors.transparent,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(
                            mode.$4,
                            color: selected
                                ? TacticalColors.accent
                                : TacticalColors.muted,
                          ),
                          const Spacer(),
                          Text(
                            mode.$2,
                            style: const TextStyle(fontWeight: FontWeight.w800),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            mode.$3,
                            style: const TextStyle(
                              color: TacticalColors.muted,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          const SizedBox(height: 14),
          Row(
            children: [
              const Expanded(
                child: Text(
                  'PRE-FLIGHT LINK CHECK REQUIRED',
                  style: TextStyle(
                    color: TacticalColors.warning,
                    fontSize: 10,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.1,
                  ),
                ),
              ),
              TacticalButton(
                label: 'CONTINUE',
                icon: Icons.arrow_forward,
                onPressed: _continueToPreflight,
              ),
            ],
          ),
        ],
      ),
    );
  }

  Future<void> _continueToPreflight() async {
    try {
      final connection = await ref.read(backendConnectionProvider.future);
      if (connection != null) {
        await ref
            .read(aeroCloudClientProvider)
            .selectFlightMode(_modes[_selected].$1);
      }
    } on Exception catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not send selected mode: $error')),
      );
      return;
    }
    if (!mounted) return;
    Navigator.of(context).pushNamed(AppRoutes.preFlight);
  }
}
