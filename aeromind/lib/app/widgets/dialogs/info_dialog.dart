import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class InfoDialog extends StatelessWidget {
  final String title;
  final String message;

  const InfoDialog({super.key, required this.title, required this.message});

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: AppColors.surface,
      title: Text(title, style: const TextStyle(color: AppColors.textPrimary)),
      content: Text(message, style: const TextStyle(color: AppColors.textSecondary)),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('OK', style: TextStyle(color: AppColors.primary)),
        ),
      ],
    );
  }
}