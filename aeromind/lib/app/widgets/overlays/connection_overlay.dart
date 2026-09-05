import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class ConnectionOverlay extends StatelessWidget {
  final bool isConnecting;

  const ConnectionOverlay({super.key, this.isConnecting = true});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black87,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(color: AppColors.primary),
            const SizedBox(height: 16),
            Text(
              isConnecting ? 'Establishing Link with Telemetry Bus...' : 'Connection Lost. Reconnecting...',
              style: const TextStyle(color: AppColors.textPrimary, fontSize: 16),
            ),
          ],
        ),
      ),
    );
  }
}