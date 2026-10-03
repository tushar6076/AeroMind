import 'package:flutter/material.dart';

class AiApplicationPage extends StatelessWidget {
  const AiApplicationPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI Applications')),
      body: const Center(child: Text('Edge AI Pipeline Status')),
    );
  }
}