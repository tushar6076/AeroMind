import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class CameraOverlay extends StatelessWidget {
  final String fps;
  final String resolution;

  const CameraOverlay({super.key, this.fps = '60 FPS', this.resolution = '1080p'});

  @override
  Widget build(BuildContext context) {
    return Positioned(
      top: 16,
      right: 16,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.black54,
          borderRadius: BorderRadius.circular(6),
        ),
        child: Text('$resolution • $fps', style: const TextStyle(color: AppColors.textPrimary, fontSize: 12)),
      ),
    );
  }
}