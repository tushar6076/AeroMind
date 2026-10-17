import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';

import '../../../../core/models/backend_status.dart';
import '../../../../core/network/flight_control_socket.dart';
import '../../../../core/network/http_client.dart';
import '../../../../core/providers/backend_providers.dart';
import '../../../../core/router/app_router.dart';
import '../../../../core/services/webrtc_service.dart';
import '../../../../core/styles/color.dart';
import '../../../../shared/widgets/buttons/tactical_button.dart';
import '../../../../shared/widgets/joysticks/joystick_left.dart';
import '../../../../shared/widgets/joysticks/joystick_right.dart';
import '../../../../shared/widgets/layout/app_scaffold.dart';
import '../../../../shared/widgets/overlays/map_overlay.dart';

class LiveFlightScreen extends ConsumerStatefulWidget {
  const LiveFlightScreen({super.key});

  @override
  ConsumerState<LiveFlightScreen> createState() => _LiveFlightScreenState();
}

class _LiveFlightScreenState extends ConsumerState<LiveFlightScreen> {
  WebRtcVideoService? _video;
  bool _connectingVideo = false;
  String? _videoError;
  bool _preview = false;
  bool _didStartVideo = false;
  Offset _leftStick = Offset.zero;
  Offset _rightStick = Offset.zero;
  FlightStatus? _flightOverride;
  AeroCloudControlSocket? _controlSocket;
  StreamSubscription<String>? _controlErrorSubscription;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _preview = ModalRoute.of(context)?.settings.arguments == true;
    if (!_didStartVideo) {
      _didStartVideo = true;
      WidgetsBinding.instance.addPostFrameCallback((_) => _connectVideo());
    }
  }

  @override
  void dispose() {
    unawaited(_video?.close());
    unawaited(_closeControlSocket());
    super.dispose();
  }

  Future<void> _connectVideo() async {
    if (!mounted) return;
    setState(() {
      _connectingVideo = true;
      _videoError = null;
    });
    final service = WebRtcVideoService(ref.read(aeroCloudClientProvider));
    _video = service;
    try {
      await service.connect();
      if (!mounted) {
        await service.close();
        return;
      }
      setState(() => _connectingVideo = false);
    } on Exception catch (error) {
      await service.close();
      if (!mounted) return;
      setState(() {
        _video = null;
        _connectingVideo = false;
        _videoError = error.toString();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final compact = MediaQuery.sizeOf(context).width < 760;
    final health = ref.watch(backendHealthProvider).asData?.value;
    final flight = ref.watch(flightStatusProvider);
    final flightStatus = flight.asData?.value ?? _flightOverride;
    final telemetry = ref.watch(telemetryProvider);
    final telemetryData = telemetry.asData?.value;
    final controlEnabled =
        !_preview &&
        flightStatus?.controlAvailable == true &&
        _controlSocket != null;

    return TacticalAppScaffold(
      title: _preview ? 'HUD Preview' : 'Live Flight HUD',
      actions: [
        Chip(
          avatar: Icon(
            _preview ? Icons.visibility_outlined : Icons.flight,
            size: 15,
          ),
          label: Text(_preview ? 'PREVIEW ONLY' : 'LIVE SESSION'),
        ),
      ],
      child: Column(
        children: [
          Expanded(
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Expanded(
                  child: _VideoPanel(
                    renderer: _video?.renderer,
                    streaming: health?.videoStreaming == true,
                    connecting: _connectingVideo,
                    error: _videoError,
                    onRetry: _connectVideo,
                    telemetry: telemetryData,
                  ),
                ),
                if (!compact) ...[
                  const SizedBox(width: 12),
                  MapOverlay(telemetry: telemetryData),
                ],
              ],
            ),
          ),
          if (compact) ...[
            const SizedBox(height: 8),
            SizedBox(height: 140, child: MapOverlay(telemetry: telemetryData)),
          ],
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              JoystickLeft(
                position: _leftStick,
                enabled: controlEnabled,
                onChanged: (position) {
                  setState(() => _leftStick = position);
                  _sendControl();
                },
              ),
              Flexible(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      _controlStatus(flightStatus, _preview),
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: TacticalColors.warning,
                        fontSize: 9,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 8),
                    _FlightAction(
                      preview: _preview,
                      flight: flightStatus,
                      onArm: () => _changeArmedState(context, arm: true),
                      onDisarm: () => _changeArmedState(context, arm: false),
                      onEnd: () => _endSession(context),
                      onClose: () => Navigator.of(context).maybePop(),
                    ),
                  ],
                ),
              ),
              JoystickRight(
                position: _rightStick,
                enabled: controlEnabled,
                onChanged: (position) {
                  setState(() => _rightStick = position);
                  _sendControl();
                },
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _controlStatus(FlightStatus? flight, bool preview) {
    if (preview) return 'PREVIEW ONLY · TRANSMITTER LOCKED';
    if (flight == null) return 'FLIGHT STATUS UNKNOWN';
    if (flight.armed && flight.controlAvailable) {
      return _controlSocket == null
          ? 'ARMED · CONTROL LINK UNAVAILABLE'
          : 'ARMED · LIVE CONTROL';
    }
    if (!flight.armingAvailable) return 'ARM CHANNEL NOT CONFIGURED';
    if (!flight.readyForFlight) return 'PREFLIGHT CHECKS FAILED';
    return 'SESSION READY · DISARMED';
  }

  Future<void> _changeArmedState(
    BuildContext context, {
    required bool arm,
  }) async {
    if (arm) {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('Arm ELRS transmitter?'),
          content: const Text(
            'Only continue after checking the area and following your '
            'flight-controller safety procedure. The backend will send the '
            'configured CRSF arm-channel value.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('CANCEL'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('ARM TRANSMITTER'),
            ),
          ],
        ),
      );
      if (!context.mounted) return;
      if (confirmed != true) return;
    }

    try {
      final client = ref.read(aeroCloudClientProvider);
      if (arm) {
        final status = await client.arm();
        if (!status.controlAvailable) {
          throw const AeroCloudException(
            'Backend did not enable live control after arming.',
          );
        }
        final socket = await AeroCloudControlSocket.connect(client);
        if (!mounted || !context.mounted) {
          await client.disarm();
          await socket.close();
          return;
        }
        _controlErrorSubscription = socket.errors.listen(_handleControlError);
        setState(() {
          _flightOverride = status;
          _controlSocket = socket;
        });
        _sendControl();
      } else {
        await client.disarm();
        await _closeControlSocket();
        final status = await client.getFlightStatus();
        if (mounted && context.mounted) {
          setState(() => _flightOverride = status);
        }
      }
      ref.invalidate(flightStatusProvider);
    } on Exception catch (error) {
      if (arm) {
        try {
          await ref.read(aeroCloudClientProvider).disarm();
        } on Exception catch (disarmError) {
          if (!mounted || !context.mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Control connection failed ($error); disarm also failed '
                '($disarmError). Verify the FC failsafe immediately.',
              ),
            ),
          );
          return;
        }
      }
      if (!mounted || !context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not ${arm ? 'arm' : 'disarm'}: $error')),
      );
    }
  }

  Future<void> _endSession(BuildContext context) async {
    try {
      await ref.read(aeroCloudClientProvider).endFlightSession();
      await _closeControlSocket();
      ref.invalidate(flightStatusProvider);
      _flightOverride = null;
      if (mounted && context.mounted) {
        await Navigator.of(context).pushNamedAndRemoveUntil(
          AppRoutes.debrief,
          ModalRoute.withName(AppRoutes.lobby),
        );
      }
    } on Exception catch (error) {
      if (!mounted || !context.mounted) return;
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Could not end session: $error')));
    }
  }

  void _sendControl() {
    final socket = _controlSocket;
    if (socket == null) return;
    try {
      socket.send(
        roll: _rightStick.dx,
        pitch: -_rightStick.dy,
        yaw: _leftStick.dx,
        throttle: _leftStick.dy,
      );
    } on StateError catch (error) {
      _handleControlError(error.toString());
    }
  }

  void _handleControlError(String message) {
    if (!mounted) return;
    unawaited(_closeControlSocket());
    setState(() {
      _controlSocket = null;
      _flightOverride = null;
    });
    ref.invalidate(flightStatusProvider);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Live control link lost: $message'),
        backgroundColor: TacticalColors.danger,
      ),
    );
  }

  Future<void> _closeControlSocket() async {
    final subscription = _controlErrorSubscription;
    _controlErrorSubscription = null;
    final socket = _controlSocket;
    _controlSocket = null;
    await subscription?.cancel();
    try {
      await socket?.close();
    } on Exception catch (error) {
      debugPrint('Could not close control socket cleanly: $error');
    }
  }
}

class _VideoPanel extends StatelessWidget {
  const _VideoPanel({
    required this.renderer,
    required this.streaming,
    required this.connecting,
    required this.error,
    required this.onRetry,
    required this.telemetry,
  });

  final RTCVideoRenderer? renderer;
  final bool streaming;
  final bool connecting;
  final String? error;
  final VoidCallback onRetry;
  final TelemetrySnapshot? telemetry;

  @override
  Widget build(BuildContext context) {
    final hasVideo = renderer?.srcObject != null;
    return Container(
      clipBehavior: Clip.antiAlias,
      decoration: BoxDecoration(
        color: const Color(0xFF05090C),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: TacticalColors.outline),
      ),
      child: Stack(
        alignment: Alignment.center,
        children: [
          if (renderer != null)
            Positioned.fill(
              child: RTCVideoView(
                renderer!,
                objectFit: RTCVideoViewObjectFit.RTCVideoViewObjectFitCover,
              ),
            ),
          if (!hasVideo)
            Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  error == null
                      ? Icons.videocam_off_outlined
                      : Icons.warning_amber,
                  color: error == null
                      ? TacticalColors.muted
                      : TacticalColors.warning,
                  size: 38,
                ),
                const SizedBox(height: 12),
                Text(
                  error != null
                      ? 'WEBRTC STREAM UNAVAILABLE'
                      : connecting
                      ? 'CONNECTING TO WEBRTC VIDEO'
                      : 'WAITING FOR WEBRTC VIDEO',
                  style: const TextStyle(
                    color: TacticalColors.text,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1.2,
                    fontSize: 11,
                  ),
                ),
                if (error != null) ...[
                  const SizedBox(height: 8),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    child: Text(
                      error!,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: TacticalColors.muted,
                        fontSize: 10,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  TextButton.icon(
                    onPressed: onRetry,
                    icon: const Icon(Icons.refresh, size: 16),
                    label: const Text('RETRY'),
                  ),
                ],
              ],
            ),
          Positioned(
            left: 14,
            top: 12,
            child: _HudReadout(label: 'ALTITUDE', value: '--'),
          ),
          Positioned(
            left: 100,
            top: 12,
            child: _HudReadout(
              label: 'BATTERY',
              value: telemetry?.batteryPercent == null
                  ? '--'
                  : '${telemetry!.batteryPercent!.toStringAsFixed(0)}%',
            ),
          ),
          Positioned(
            right: 14,
            top: 12,
            child: _HudReadout(
              label: 'LINK',
              value: telemetry?.linkQuality == null
                  ? 'NO LINK'
                  : '${telemetry!.linkQuality}%',
            ),
          ),
          Positioned(
            right: 14,
            bottom: 12,
            child: _HudReadout(label: 'DETECTIONS', value: '--'),
          ),
          if (streaming && hasVideo)
            const Positioned(
              left: 14,
              bottom: 12,
              child: _HudReadout(label: 'VIDEO', value: 'LIVE'),
            ),
        ],
      ),
    );
  }
}

class _HudReadout extends StatelessWidget {
  const _HudReadout({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: TacticalColors.muted,
            fontSize: 8,
            letterSpacing: 1,
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            color: TacticalColors.text,
            fontSize: 10,
            fontWeight: FontWeight.w900,
          ),
        ),
      ],
    );
  }
}

class _FlightAction extends StatelessWidget {
  const _FlightAction({
    required this.preview,
    required this.flight,
    required this.onArm,
    required this.onDisarm,
    required this.onEnd,
    required this.onClose,
  });

  final bool preview;
  final FlightStatus? flight;
  final VoidCallback onArm;
  final VoidCallback onDisarm;
  final VoidCallback onEnd;
  final VoidCallback onClose;

  @override
  Widget build(BuildContext context) {
    if (preview) {
      return TacticalButton(
        label: 'CLOSE PREVIEW',
        icon: Icons.close,
        filled: false,
        onPressed: onClose,
      );
    }
    if (flight?.armed == true) {
      return TacticalButton(
        label: 'DISARM',
        icon: Icons.power_settings_new,
        onPressed: onDisarm,
      );
    }
    return Wrap(
      alignment: WrapAlignment.center,
      spacing: 8,
      children: [
        TacticalButton(
          label: 'ARM',
          icon: Icons.power,
          onPressed:
              flight?.sessionActive == true &&
                  flight?.readyForFlight == true &&
                  flight?.armingAvailable == true
              ? onArm
              : null,
        ),
        TacticalButton(
          label: 'END SESSION',
          icon: Icons.stop_circle_outlined,
          filled: false,
          onPressed: flight?.sessionActive == true ? onEnd : onClose,
        ),
      ],
    );
  }
}
