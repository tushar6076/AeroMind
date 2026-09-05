import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../routes/app_routes.dart';

class SettingsSideNav extends StatelessWidget {
  final int selectedIndex;
  final ValueChanged<int> onItemSelected;
  final VoidCallback? onLogout;

  const SettingsSideNav({
    super.key,
    required this.selectedIndex,
    required this.onItemSelected,
    this.onLogout,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 230,
      color: AppColors.background, // Ensures the background color is consistent with the rest of the app
      child: Material(
        color: Colors.transparent, // Ensures ListTile ink and selectedTileColor paint correctly
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with Back Arrow
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
              color: AppColors.background,
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary, size: 20),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    tooltip: 'Back to Home',
                    onPressed: () {
                      if (Navigator.canPop(context)) {
                        Navigator.pop(context);
                      } else {
                        Navigator.pushReplacementNamed(context, AppRoutes.home);
                      }
                    },
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    'Settings',
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            ),
            const Divider(height: 1, color: AppColors.surface),
            // Sub-pages list
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Column(
                  children: [
                    _buildNavItem(
                      index: 0,
                      icon: Icons.dashboard_outlined,
                      title: 'Overview',
                    ),
                    _buildNavItem(
                      index: 1,
                      icon: Icons.person_outline,
                      title: 'Edit Profile',
                    ),
                    _buildNavItem(
                      index: 2,
                      icon: Icons.lock_outline,
                      title: 'Change Password',
                    ),
                    _buildNavItem(
                      index: 3,
                      icon: Icons.tune_outlined,
                      title: 'Preferences',
                    ),
                    _buildNavItem(
                      index: 4,
                      icon: Icons.history,
                      title: 'Flight History',
                    ),
                  ],
                ),
              ),
            ),
            const Divider(color: AppColors.background, height: 1),
            // Footer Logout Action
            SizedBox(
              height: 44,
              child: InkWell(
                onTap: () {
                  if (onLogout != null) {
                    onLogout!();
                  } else {
                    Navigator.pushNamedAndRemoveUntil(
                      context,
                      AppRoutes.login,
                      (route) => false,
                    );
                  }
                },
                child: const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      Icon(Icons.logout, color: Colors.redAccent, size: 18),
                      SizedBox(width: 12),
                      Text(
                        'Logout',
                        style: TextStyle(
                          color: Colors.redAccent,
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 4),
          ],
        ),
      ),
    );
  }

  Widget _buildNavItem({
    required int index,
    required IconData icon,
    required String title,
  }) {
    final isSelected = selectedIndex == index;
    final color = isSelected ? AppColors.primary : AppColors.textSecondary;
    final textColor = isSelected ? AppColors.primary : AppColors.textPrimary;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      child: SizedBox(
        height: 38,
        child: Material(
          color: isSelected ? AppColors.primary.withValues(alpha: 0.12) : Colors.transparent,
          borderRadius: BorderRadius.circular(6),
          child: InkWell(
            borderRadius: BorderRadius.circular(6),
            onTap: () => onItemSelected(index),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Row(
                children: [
                  Icon(icon, color: color, size: 18),
                  const SizedBox(width: 12),
                  Text(
                    title,
                    style: TextStyle(
                      color: textColor,
                      fontSize: 13,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}