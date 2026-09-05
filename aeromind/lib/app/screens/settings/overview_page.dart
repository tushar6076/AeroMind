import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/constants/app_colors.dart';
import '../../providers/auth_provider.dart';
import '../../widgets/buttons/primary_button.dart';
import '../../widgets/dialogs/confirm_dialog.dart';

class SettingsOverviewPage extends ConsumerWidget {
  const SettingsOverviewPage({super.key});

  String _getInitial(String? fullName, String? email) {
    if (fullName != null && fullName.trim().isNotEmpty) {
      return fullName.trim()[0].toUpperCase();
    }
    if (email != null && email.trim().isNotEmpty) {
      return email.trim()[0].toUpperCase();
    }
    return 'U';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(authProvider).user;
    final fullName = user?.fullName;
    final email = user?.email;

    final initial = _getInitial(fullName, email);
    final displayName = (fullName != null && fullName.trim().isNotEmpty)
        ? fullName
        : 'AeroMind Operator';
    final displayEmail = (email != null && email.trim().isNotEmpty)
        ? email
        : 'operator@aeromind.dev';

    return SingleChildScrollView(
      padding: const EdgeInsets.all(32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Account Overview',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppColors.textSecondary.withValues(alpha: 0.1)),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 32,
                  backgroundColor: AppColors.primary.withValues(alpha: 0.2),
                  child: Text(
                    initial,
                    style: const TextStyle(fontSize: 24, color: AppColors.primary, fontWeight: FontWeight.bold),
                  ),
                ),
                const SizedBox(width: 20),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        displayName,
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        displayEmail,
                        style: const TextStyle(fontSize: 14, color: AppColors.textSecondary),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 40),
          // Account Management & Danger Zone
          const Text(
            'Danger Zone',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.redAccent),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.redAccent.withValues(alpha: 0.05),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.redAccent.withValues(alpha: 0.2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Delete Account',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                ),
                const SizedBox(height: 6),
                const Text(
                  'Deleting your account will permanently invalidate all API tokens and telemetry logs. This action cannot be undone.',
                  style: TextStyle(color: AppColors.textSecondary, fontSize: 13, height: 1.4),
                ),
                const SizedBox(height: 16),
                PrimaryButton(
                  text: 'Delete Account',
                  backgroundColor: Colors.redAccent.withValues(alpha: 0.2),
                  onPressed: () async {
                    await showDialog(
                      context: context,
                      builder: (dialogContext) => ConfirmDialog(
                        title: 'Confirm Account Deletion',
                        message: 'Are you sure you want to delete your account permanently?',
                        confirmText: 'Delete Permanently',
                        onConfirm: () => Navigator.of(dialogContext).pop(),
                      ),
                    );
                  },
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}