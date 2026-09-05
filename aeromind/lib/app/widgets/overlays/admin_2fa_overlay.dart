import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class Admin2FAOverlay extends StatelessWidget {
  final VoidCallback onVerified;

  const Admin2FAOverlay({super.key, required this.onVerified});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black.withValues(alpha: 0.85),
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.security, size: 56, color: AppColors.primary),
              const SizedBox(height: 16),
              const Text('Admin Verification', style: TextStyle(color: AppColors.textPrimary, fontSize: 20, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              const Text('Enter 2FA Code to Access High-Level Fleet Actions', style: TextStyle(color: AppColors.textSecondary), textAlign: TextAlign.center),
              const SizedBox(height: 24),
              ElevatedButton(
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.primary),
                onPressed: onVerified,
                child: const Text('Verify Access'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}