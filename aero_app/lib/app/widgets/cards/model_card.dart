import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class ModelCard extends StatelessWidget {
  final String modelName;
  final String description;
  final String version;
  final bool isActive;
  final VoidCallback onTap;

  const ModelCard({
    super.key,
    required this.modelName,
    required this.description,
    required this.version,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.surface,
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        onTap: onTap,
        title: Row(
          children: [
            Text(modelName, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold)),
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: AppColors.surfaceLight,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(version, style: const TextStyle(color: AppColors.textSecondary, fontSize: 10)),
            ),
          ],
        ),
        subtitle: Text(description, style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
        trailing: Container(
          width: 10,
          height: 10,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: isActive ? AppColors.success : AppColors.textMuted,
          ),
        ),
      ),
    );
  }
}