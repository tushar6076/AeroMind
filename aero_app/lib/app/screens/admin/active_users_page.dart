import 'package:flutter/material.dart';

class ActiveUsersPage extends StatelessWidget {
  const ActiveUsersPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Active Users')),
      body: const Center(child: Text('Active Pilots & Admins')),
    );
  }
}