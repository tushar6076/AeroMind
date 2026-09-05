import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class MapOverlay extends StatelessWidget {
  const MapOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 120,
      height: 120,
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primary, width: 1.5),
      ),
      child: const Center(
        child: Icon(Icons.map_outlined, color: AppColors.textSecondary, size: 36),
      ),
    );
  }
}