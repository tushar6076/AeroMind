import 'dart:async';
import 'dart:convert';

import 'package:web_socket_channel/web_socket_channel.dart';

import 'http_client.dart';

class AeroCloudControlSocket {
  AeroCloudControlSocket._(this._channel) {
    _subscription = _channel.stream.listen(
      _handleMessage,
      onError: (Object error, StackTrace stackTrace) {
        _errors.add('Control connection error: $error');
      },
      onDone: () {
        if (!_closed) _errors.add('Control connection was closed.');
      },
    );
    _heartbeat = Timer.periodic(
      const Duration(milliseconds: 200),
      (_) => _sendLatest(),
    );
  }

  final WebSocketChannel _channel;
  final StreamController<String> _errors = StreamController<String>.broadcast();
  late final StreamSubscription<dynamic> _subscription;
  late final Timer _heartbeat;
  bool _closed = false;
  double _roll = 0;
  double _pitch = 0;
  double _yaw = 0;
  double _throttle = 0;

  Stream<String> get errors => _errors.stream;

  static Future<AeroCloudControlSocket> connect(AeroCloudClient client) async {
    final channel = WebSocketChannel.connect(
      client.flightControlSocketUri(),
      protocols: ['aeromind-control', client.controlSocketProtocol],
    );
    try {
      await channel.ready.timeout(const Duration(seconds: 5));
    } catch (error, stackTrace) {
      await channel.sink.close();
      Error.throwWithStackTrace(error, stackTrace);
    }
    return AeroCloudControlSocket._(channel);
  }

  void send({
    required double roll,
    required double pitch,
    required double yaw,
    required double throttle,
  }) {
    if (_closed) throw StateError('Flight control socket is closed.');
    _roll = roll;
    _pitch = pitch;
    _yaw = yaw;
    _throttle = throttle;
    _sendLatest();
  }

  void _sendLatest() {
    if (_closed) return;
    _channel.sink.add(
      jsonEncode({
        'roll': _roll,
        'pitch': _pitch,
        'yaw': _yaw,
        'throttle': _throttle,
      }),
    );
  }

  Future<void> close() async {
    if (_closed) return;
    _closed = true;
    _heartbeat.cancel();
    await _subscription.cancel();
    await _channel.sink.close();
    await _errors.close();
  }

  void _handleMessage(dynamic message) {
    if (message is! String) {
      _errors.add('Unexpected binary response from control service.');
      return;
    }
    try {
      final decoded = jsonDecode(message);
      if (decoded is Map && decoded['error'] is String) {
        _errors.add(decoded['error'] as String);
      }
    } on FormatException catch (error) {
      _errors.add('Invalid response from control service: $error');
    }
  }
}
