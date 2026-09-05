import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../constants/api_endpoints.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  Timer? _pingTimer;

  void connect(String clientId) {
    try {
      final wsUri = Uri.parse(ApiEndpoints.uplinkWs(clientId));
      _channel = WebSocketChannel.connect(wsUri);
      _startHeartbeat();
    } catch (e) {
      // Connection errors handled upstream
    }
  }

  void _startHeartbeat() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 15), (_) {
      send({'type': 'ping', 'timestamp': DateTime.now().millisecondsSinceEpoch});
    });
  }

  void send(Map<String, dynamic> data) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode(data));
    }
  }

  Stream? get stream => _channel?.stream;

  void disconnect() {
    _pingTimer?.cancel();
    _channel?.sink.close();
    _channel = null;
  }
}