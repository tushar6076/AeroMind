import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class JoystickLeft extends StatelessWidget {
  final Function(double throttle, double yaw)? onChanged;

  const JoystickLeft({super.key, this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 140,
      height: 140,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.surface,
        border: Border.all(color: AppColors.surfaceLight, width: 2),
      ),
      child: Center(
        child: Container(
          width: 50,
          height: 50,
          decoration: const BoxDecoration(
            shape: BoxShape.circle,
            color: AppColors.primary,
          ),
          child: const Icon(Icons.height, color: AppColors.textPrimary, size: 28),
        ),
      ),
    );
  }
}