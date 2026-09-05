import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../routes/app_routes.dart';

class AdminSideNav extends StatelessWidget {
  const AdminSideNav({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: AppColors.surface,
      child: ListView(
        padding: EdgeInsets.zero,
        children: [
          const DrawerHeader(
            decoration: BoxDecoration(color: AppColors.background),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.admin_panel_settings, size: 40, color: AppColors.primary),
                SizedBox(height: 8),
                Text('Admin Workspace', style: TextStyle(color: AppColors.textPrimary, fontSize: 18, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          ListTile(
            leading: const Icon(Icons.dashboard_outlined, color: AppColors.textSecondary),
            title: const Text('Overview', style: TextStyle(color: AppColors.textPrimary)),
            onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.adminOverview),
          ),
          ListTile(
            leading: const Icon(Icons.people_outline, color: AppColors.textSecondary),
            title: const Text('Active Users', style: TextStyle(color: AppColors.textPrimary)),
            onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.adminActiveUsers),
          ),
          ListTile(
            leading: const Icon(Icons.tune_outlined, color: AppColors.textSecondary),
            title: const Text('Fleet Control', style: TextStyle(color: AppColors.textPrimary)),
            onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.adminControl),
          ),
          ListTile(
            leading: const Icon(Icons.settings_outlined, color: AppColors.textSecondary),
            title: const Text('Settings', style: TextStyle(color: AppColors.textPrimary)),
            onTap: () => Navigator.pushReplacementNamed(context, AppRoutes.adminAiManagement),
          ),
        ],
      ),
    );
  }
}