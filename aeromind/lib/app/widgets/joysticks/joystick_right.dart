import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class JoystickRight extends StatelessWidget {
  final Function(double pitch, double roll)? onChanged;

  const JoystickRight({super.key, this.onChanged});

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
            color: AppColors.accent,
          ),
          child: const Icon(Icons.open_with, color: AppColors.textPrimary, size: 28),
        ),
      ),
    );
  }
}