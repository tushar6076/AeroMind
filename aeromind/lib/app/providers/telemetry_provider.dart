import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../core/services/websocket_service.dart';

final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final service = WebSocketService();
  ref.onDispose(() => service.disconnect());
  return service;
});

final telemetryStreamProvider = StreamProvider.family<dynamic, String>((ref, clientId) {
  final wsService = ref.watch(webSocketServiceProvider);
  wsService.connect(clientId);
  return wsService.stream?.cast<dynamic>() ?? const Stream.empty();
});