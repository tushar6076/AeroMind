import 'package:flutter/material.dart';

import '../../core/constants/app_colors.dart';
import '../../widgets/drawer/settings_side_nav.dart';
import 'change_password_page.dart';
import 'edit_profile_page.dart';
import 'flight_history_page.dart';
import 'overview_page.dart';
import 'preferences_page.dart';

class SettingsLayout extends StatefulWidget {
  final int initialIndex;

  const SettingsLayout({
    super.key,
    this.initialIndex = 0,
  });

  @override
  State<SettingsLayout> createState() => _SettingsLayoutState();
}

class _SettingsLayoutState extends State<SettingsLayout> {
  late int _selectedIndex;

  final List<Widget> _pages = const [
    SettingsOverviewPage(),
    SettingsEditProfilePage(),
    SettingsChangePasswordPage(),
    SettingsPreferencesPage(),
    SettingsFlightHistoryPage(),
  ];

  @override
  void initState() {
    super.initState();
    _selectedIndex = widget.initialIndex;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Row(
          children: [
            SettingsSideNav(
              selectedIndex: _selectedIndex,
              onItemSelected: (index) {
                setState(() {
                  _selectedIndex = index;
                });
              },
            ),
            const VerticalDivider(width: 1, color: AppColors.surface),
            Expanded(
              child: IndexedStack(
                index: _selectedIndex,
                children: _pages,
              ),
            ),
          ],
        ),
      ),
    );
  }
}