import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'api_service.dart';
import '../constants/api_endpoints.dart';

class WebRTCService {
  final ApiService _apiService;
  RTCPeerConnection? _peerConnection;
  RTCVideoRenderer localRenderer = RTCVideoRenderer();
  RTCVideoRenderer remoteRenderer = RTCVideoRenderer();

  WebRTCService(this._apiService);

  Future<void> initializeRenderers() async {
    await localRenderer.initialize();
    await remoteRenderer.initialize();
  }

  Future<void> createOffer() async {
    final configuration = <String, dynamic>{
      'iceServers': [
        {'urls': 'stun:stun.l.google.com:19302'},
      ]
    };

    _peerConnection = await createPeerConnection(configuration);

    _peerConnection?.onIceCandidate = (candidate) async {
      await _apiService.sendFlightCommand(
        ApiEndpoints.streamIceCandidate,
        payload: {
          'candidate': candidate.candidate,
          'sdpMid': candidate.sdpMid,
          'sdpMLineIndex': candidate.sdpMLineIndex,
        },
      );
    };

    _peerConnection?.onTrack = (event) {
      if (event.track.kind == 'video') {
        remoteRenderer.srcObject = event.streams[0];
      }
    };

    RTCSessionDescription offer = await _peerConnection!.createOffer();
    await _peerConnection!.setLocalDescription(offer);

    // Dispatch SDP Offer to Drone Backend
    await _apiService.sendFlightCommand(
      ApiEndpoints.streamOffer,
      payload: {'sdp': offer.sdp, 'type': offer.type},
    );
  }

  Future<void> setRemoteAnswer(String sdp, String type) async {
    final answer = RTCSessionDescription(sdp, type);
    await _peerConnection?.setRemoteDescription(answer);
  }

  Future<void> addIceCandidate(Map<String, dynamic> candidateData) async {
    final candidate = RTCIceCandidate(
      candidateData['candidate'],
      candidateData['sdpMid'],
      candidateData['sdpMLineIndex'],
    );
    await _peerConnection?.addCandidate(candidate);
  }

  Future<void> dispose() async {
    await localRenderer.dispose();
    await remoteRenderer.dispose();
    await _peerConnection?.close();
    _peerConnection = null;
  }
}