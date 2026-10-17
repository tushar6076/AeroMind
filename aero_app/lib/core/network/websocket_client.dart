import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import '../models/backend_status.dart';
import 'http_client.dart';

class AeroCloudWebSocketClient {
  AeroCloudWebSocketClient(this._client);

  final AeroCloudClient _client;

  Stream<TelemetrySnapshot> telemetry() async* {
    final channel = WebSocketChannel.connect(_client.telemetrySocketUri());
    try {
      await channel.ready.timeout(const Duration(seconds: 5));
      await for (final message in channel.stream) {
        if (message is! String) {
          throw const FormatException('Unexpected binary telemetry message.');
        }
        final decoded = jsonDecode(message);
        if (decoded is! Map || decoded['type'] != 'telemetry') {
          throw const FormatException('Unexpected Aero Cloud telemetry shape.');
        }
        final data = decoded['data'];
        if (data is! Map) {
          throw const FormatException('Telemetry data must be a JSON object.');
        }
        yield TelemetrySnapshot.fromJson(Map<String, dynamic>.from(data));
      }
    } on TimeoutException {
      throw const AeroCloudException(
        'Telemetry WebSocket connection timed out.',
      );
    } finally {
      await channel.sink.close();
    }
  }
}
