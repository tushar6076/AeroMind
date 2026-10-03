import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/auth_provider.dart';
import '../../routes/app_routes.dart';

class SplashScreen extends ConsumerWidget {
  const SplashScreen({super.key});

  void _navigateToNext(BuildContext context, bool isAuthenticated) {
    Navigator.pushReplacementNamed(
      context,
      isAuthenticated ? AppRoutes.home : AppRoutes.login,
    );
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to authentication state changes cleanly
    ref.listen(authProvider, (previous, next) {
      if (!next.isLoading) {
        _navigateToNext(context, next.isAuthenticated);
      }
    });

    // Fallback check if state was already resolved before build
    final authState = ref.watch(authProvider);
    if (!authState.isLoading) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _navigateToNext(context, authState.isAuthenticated);
      });
    }

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40.0, vertical: 20.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Spacer(),

              // BRANDING LOGO & TITLE
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(
                        color: AppColors.primary.withValues(alpha: 0.4),
                        width: 1.5,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withValues(alpha: 0.25),
                          blurRadius: 16,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                    child: const Icon(
                      Icons.flight_takeoff,
                      size: 48,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(width: 20),
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'AEROMIND',
                        style: TextStyle(
                          color: AppColors.textPrimary,
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 2.5,
                        ),
                      ),
                      Text(
                        'AUTONOMOUS FLIGHT SYSTEM',
                        style: TextStyle(
                          color: const Color(0xFF00E5FF),
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.5,
                        ),
                      ),
                    ],
                  ),
                ],
              ),

              const Spacer(),

              // TACTICAL PROGRESS INDICATOR
              SizedBox(
                width: 280,
                child: Column(
                  children: [
                    const LinearProgressIndicator(
                      color: AppColors.primary,
                      backgroundColor: Colors.white10,
                      minHeight: 3,
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: const [
                        Text(
                          'INITIALIZING HUD...',
                          style: TextStyle(
                            color: Colors.white54,
                            fontSize: 10,
                            fontFamily: 'monospace',
                            letterSpacing: 1.0,
                          ),
                        ),
                        Text(
                          'v1.0.4',
                          style: TextStyle(
                            color: Colors.white38,
                            fontSize: 10,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}