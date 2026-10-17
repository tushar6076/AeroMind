import 'package:flutter/material.dart';

import '../../features/edge_ai/presentation/screens/ai_loadout_screen.dart';
import '../../features/flight/presentation/screens/flight_mode_screen.dart';
import '../../features/gameplay/presentation/screens/live_flight_screen.dart';
import '../../features/gameplay/presentation/screens/post_flight_screen.dart';
import '../../features/gameplay/presentation/screens/pre_flight_screen.dart';
import '../../features/lobby/presentation/screens/lobby_screen.dart';
import '../../features/settings/presentation/screens/rig_settings_screen.dart';
import '../../features/vault/presentation/screens/recon_vault_screen.dart';

abstract final class AppRoutes {
  static const lobby = '/';
  static const flightModes = '/flight-modes';
  static const edgeAi = '/edge-ai';
  static const vault = '/vault';
  static const settings = '/settings';
  static const preFlight = '/pre-flight';
  static const liveFlight = '/live-flight';
  static const debrief = '/debrief';
}

abstract final class AppRouter {
  static Route<dynamic> onGenerateRoute(RouteSettings settings) {
    final Widget page = switch (settings.name) {
      AppRoutes.lobby => const LobbyScreen(),
      AppRoutes.flightModes => const FlightModeScreen(),
      AppRoutes.edgeAi => const AiLoadoutScreen(),
      AppRoutes.vault => const ReconVaultScreen(),
      AppRoutes.settings => const RigSettingsScreen(),
      AppRoutes.preFlight => const PreFlightScreen(),
      AppRoutes.liveFlight => const LiveFlightScreen(),
      AppRoutes.debrief => const PostFlightScreen(),
      _ => _UnknownRouteScreen(routeName: settings.name),
    };

    return MaterialPageRoute<void>(builder: (_) => page, settings: settings);
  }
}

class _UnknownRouteScreen extends StatelessWidget {
  const _UnknownRouteScreen({required this.routeName});

  final String? routeName;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(child: Text('Route not found: ${routeName ?? '(unnamed)'}')),
    );
  }
}
