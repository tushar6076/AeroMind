import 'dart:async';

import 'package:flutter_webrtc/flutter_webrtc.dart';

import '../network/http_client.dart';

class WebRtcVideoService {
  WebRtcVideoService(this._client);

  final AeroCloudClient _client;
  final RTCVideoRenderer renderer = RTCVideoRenderer();
  RTCPeerConnection? _peer;
  bool _rendererInitialized = false;

  Future<void> connect() async {
    try {
      await renderer.initialize();
      _rendererInitialized = true;
      final peer = await createPeerConnection(const {
        'iceServers': <Map<String, dynamic>>[],
      });
      _peer = peer;
      peer.onTrack = (event) {
        if (event.streams.isNotEmpty) {
          renderer.srcObject = event.streams.first;
        }
      };

      await peer.addTransceiver(
        kind: RTCRtpMediaType.RTCRtpMediaTypeVideo,
        init: RTCRtpTransceiverInit(direction: TransceiverDirection.RecvOnly),
      );
      final offer = await peer.createOffer();
      final gatheringComplete = Completer<void>();
      peer.onIceGatheringState = (state) {
        if (state == RTCIceGatheringState.RTCIceGatheringStateComplete &&
            !gatheringComplete.isCompleted) {
          gatheringComplete.complete();
        }
      };
      await peer.setLocalDescription(offer);
      await Future.any([
        gatheringComplete.future,
        Future<void>.delayed(const Duration(seconds: 5)),
      ]);

      final localDescription = await peer.getLocalDescription();
      if (localDescription?.sdp == null || localDescription!.sdp!.isEmpty) {
        throw const AeroCloudException('WebRTC did not produce a local offer.');
      }
      final answer = await _client.createVideoAnswer(
        sdp: localDescription.sdp!,
        type: localDescription.type ?? 'offer',
      );
      if (answer['sdp'] is! String || answer['type'] is! String) {
        throw const AeroCloudException(
          'Aero Cloud returned an invalid WebRTC answer.',
        );
      }
      await peer.setRemoteDescription(
        RTCSessionDescription(
          answer['sdp'] as String,
          answer['type'] as String,
        ),
      );
    } on Exception {
      await close();
      rethrow;
    }
  }

  Future<void> close() async {
    if (_rendererInitialized) renderer.srcObject = null;
    await _peer?.close();
    _peer = null;
    if (_rendererInitialized) {
      await renderer.dispose();
      _rendererInitialized = false;
    }
  }
}
