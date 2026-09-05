import 'package:flutter/material.dart';

import '../../core/constants/app_colors.dart';

class SettingsPreferencesPage extends StatefulWidget {
  const SettingsPreferencesPage({super.key});

  @override
  State<SettingsPreferencesPage> createState() => _SettingsPreferencesPageState();
}

class _SettingsPreferencesPageState extends State<SettingsPreferencesPage> {
  bool _enableTelemetryLogging = true;
  bool _enableAutoRtl = true;

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Preferences',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
          ),
          const SizedBox(height: 16),
          SwitchListTile(
            title: const Text('Enable Local Telemetry Logs', style: TextStyle(color: Colors.white)),
            subtitle: const Text('Save telemetry state streams locally on client', style: TextStyle(color: AppColors.textSecondary)),
            activeThumbColor: AppColors.primary,
            value: _enableTelemetryLogging,
            onChanged: (val) => setState(() => _enableTelemetryLogging = val),
          ),
          SwitchListTile(
            title: const Text('Auto RTL on Connection Loss', style: TextStyle(color: Colors.white)),
            subtitle: const Text('Trigger Return To Launch if signal drops below 10%', style: TextStyle(color: AppColors.textSecondary)),
            activeThumbColor: AppColors.primary,
            value: _enableAutoRtl,
            onChanged: (val) => setState(() => _enableAutoRtl = val),
          ),
        ],
      ),
    );
  }
}