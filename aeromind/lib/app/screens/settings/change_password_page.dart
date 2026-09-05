import 'package:flutter/material.dart';

import '../../core/constants/app_colors.dart';
import '../../widgets/buttons/primary_button.dart';

class SettingsChangePasswordPage extends StatelessWidget {
  const SettingsChangePasswordPage({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Change Password',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
          ),
          const SizedBox(height: 24),
          _buildPasswordField('Current Password'),
          const SizedBox(height: 16),
          _buildPasswordField('New Password'),
          const SizedBox(height: 16),
          _buildPasswordField('Confirm New Password'),
          const SizedBox(height: 24),
          PrimaryButton(
            text: 'Update Password',
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Password updated successfully.')),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildPasswordField(String label) {
    return TextField(
      obscureText: true,
      style: const TextStyle(color: Colors.white),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: AppColors.textSecondary),
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide(color: AppColors.textSecondary.withValues(alpha: 0.2)),
        ),
        focusedBorder: const OutlineInputBorder(
          borderSide: BorderSide(color: AppColors.primary),
        ),
      ),
    );
  }
}