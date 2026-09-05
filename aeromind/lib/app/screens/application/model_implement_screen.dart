import 'package:flutter/material.dart';

class ModelImplementScreen extends StatelessWidget {
  const ModelImplementScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Deploy Model')),
      body: const Center(child: Text('Deploy to Drone Edge Hardware')),
    );
  }
}