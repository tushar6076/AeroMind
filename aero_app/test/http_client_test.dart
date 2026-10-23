import 'dart:convert';

import 'package:aero_app/core/network/http_client.dart';
import 'package:aero_app/core/services/backend_connection.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  test('REST and control socket use the configured backend token', () async {
    late http.Request request;
    final client = AeroCloudClient(
      connection: BackendConnection(
        baseUri: Uri.parse('http://edge.local:8100'),
        accessToken: 'test-token',
      ),
      client: MockClient((capturedRequest) async {
        request = capturedRequest;
        return http.Response(
          jsonEncode({
            'session_active': false,
            'armed': false,
            'arming_available': false,
            'selected_mode': 'orbit',
            'control_available': false,
            'ready_for_flight': false,
            'detail': 'Flight mode selected.',
          }),
          200,
          headers: {'content-type': 'application/json'},
        );
      }),
    );
    addTearDown(client.close);

    final status = await client.selectFlightMode('orbit');

    expect(status.selectedMode, 'orbit');
    expect(request.method, 'POST');
    expect(request.url.path, '/api/v1/flight/mode');
    expect(request.headers['Authorization'], 'Bearer test-token');
    expect(
      client.flightControlSocketUri().toString(),
      'ws://edge.local:8100/api/v1/flight/control/ws',
    );
    expect(client.controlSocketProtocol, 'aeromind-auth-dGVzdC10b2tlbg');
  });
}
