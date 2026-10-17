import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router/app_router.dart';
import 'core/styles/theme.dart';

class AeroMindApp extends ConsumerWidget {
  const AeroMindApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: 'AeroMind GCS',
      debugShowCheckedModeBanner: false,
      theme: TacticalTheme.darkTheme,
      initialRoute: AppRoutes.lobby,
      onGenerateRoute: AppRouter.onGenerateRoute,
    );
  }
}
