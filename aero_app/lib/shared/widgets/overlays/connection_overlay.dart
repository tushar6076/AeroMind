import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/models/backend_status.dart';
import '../../../core/providers/backend_providers.dart';
import '../../../core/services/backend_connection.dart';
import '../../../core/styles/color.dart';

class ConnectionOverlay extends ConsumerStatefulWidget {
  const ConnectionOverlay({super.key});

  static Future<void> show(BuildContext context) {
    return showDialog<void>(
      context: context,
      builder: (_) => const Dialog(child: ConnectionOverlay()),
    );
  }

  @override
  ConsumerState<ConnectionOverlay> createState() => _ConnectionOverlayState();
}

class _ConnectionOverlayState extends ConsumerState<ConnectionOverlay> {
  final _urlController = TextEditingController();
  final _tokenController = TextEditingController();
  bool _loadedStoredSettings = false;
  bool _saving = false;
  String? _saveError;

  @override
  void dispose() {
    _urlController.dispose();
    _tokenController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final connection = ref.watch(backendConnectionProvider);
    final health = ref.watch(backendHealthProvider);
    final saved = connection.asData?.value;
    if (saved != null && !_loadedStoredSettings) {
      _loadedStoredSettings = true;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!mounted) return;
        _urlController.text = saved.baseUri.toString();
        _tokenController.text = saved.accessToken ?? '';
      });
    }
    final status = health.asData?.value;

    return ConstrainedBox(
      constraints: BoxConstraints(
        maxWidth: 480,
        maxHeight: MediaQuery.sizeOf(context).height * 0.85,
      ),
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                children: [
                  const Icon(Icons.hub_outlined, color: TacticalColors.accent),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Connection monitor',
                      style: Theme.of(context).textTheme.titleLarge
                          ?.copyWith(fontWeight: FontWeight.w800),
                    ),
                  ),
                  IconButton(
                    tooltip: 'Close',
                    onPressed: () => Navigator.of(context).pop(),
                    icon: const Icon(Icons.close),
                  ),
                ],
              ),
              const SizedBox(height: 14),
              _LinkStatus(
                icon: status?.backendOnline == true
                    ? Icons.cloud_done
                    : Icons.cloud_off,
                ready: status?.backendOnline,
                label: 'Aero Cloud',
                value: connection.isLoading
                    ? 'Loading saved connection'
                    : connection.hasError
                    ? 'Saved settings could not be loaded'
                    : status?.backendOnline == true
                    ? 'Connected to ${saved?.baseUri.host}'
                    : saved == null
                    ? 'Backend address is not configured'
                    : health.hasError
                    ? health.error.toString()
                    : 'Checking backend service',
              ),
              _LinkStatus(
                icon: status?.elrsConnected == true
                    ? Icons.sensors
                    : Icons.sensors_off,
                ready: status?.elrsConnected,
                label: 'ELRS bridge',
                value: _elrsStatus(status),
              ),
              _LinkStatus(
                icon: status?.videoInputAvailable == true
                    ? Icons.videocam
                    : Icons.videocam_off,
                ready: status?.videoInputAvailable,
                label: '5.8 GHz video',
                value: _videoStatus(status),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _urlController,
                keyboardType: TextInputType.url,
                decoration: const InputDecoration(
                  labelText: 'Aero Cloud URL',
                  hintText: 'http://<edge-computer-lan-ip>:8100',
                  prefixIcon: Icon(Icons.link),
                ),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _tokenController,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Backend access token',
                  hintText: 'API_ACCESS_TOKEN from backend configuration',
                  prefixIcon: Icon(Icons.key),
                ),
              ),
              if (_saveError != null) ...[
                const SizedBox(height: 8),
                Text(
                  _saveError!,
                  style: const TextStyle(color: TacticalColors.danger),
                ),
              ],
              const SizedBox(height: 10),
              const Text(
                'The app will connect through backend services. It will not '
                'open a direct drone-side connection.',
                style: TextStyle(color: TacticalColors.muted, height: 1.45),
              ),
              const SizedBox(height: 18),
              Row(
                mainAxisAlignment: MainAxisAlignment.end,
                children: [
                  if (saved != null)
                    TextButton(
                      onPressed: _saving ? null : _clearSettings,
                      child: const Text('DISCONNECT'),
                    ),
                  TextButton(
                    onPressed: () => Navigator.of(context).pop(),
                    child: const Text('CLOSE'),
                  ),
                  const SizedBox(width: 8),
                  FilledButton.icon(
                    onPressed: _saving ? null : _saveSettings,
                    icon: _saving
                        ? const SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : const Icon(Icons.wifi_tethering, size: 17),
                    label: const Text('SAVE & CONNECT'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  String _elrsStatus(BackendHealth? status) {
    if (status == null) return 'Awaiting backend diagnostics';
    if (!status.elrsConfigured) return 'CRSF serial port not configured';
    if (!status.elrsConnected) return 'Transmitter serial link unavailable';
    return status.elrsLinkQuality == null
        ? 'Serial link open; waiting for RF telemetry'
        : 'RF link quality ${status.elrsLinkQuality}%';
  }

  String _videoStatus(BackendHealth? status) {
    if (status == null) return 'Awaiting backend diagnostics';
    if (!status.videoInputConfigured) return 'UVC input not configured';
    if (!status.videoInputAvailable) return 'Capture device unavailable';
    return status.videoStreaming
        ? 'WebRTC stream active'
        : 'Capture device ready';
  }

  Future<void> _saveSettings() async {
    setState(() {
      _saving = true;
      _saveError = null;
    });
    try {
      await ref
          .read(backendConnectionProvider.notifier)
          .configure(
            url: _urlController.text,
            accessToken: _tokenController.text,
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Backend connection settings saved.')),
      );
    } on Exception catch (error) {
      if (mounted) setState(() => _saveError = error.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  Future<void> _clearSettings() async {
    setState(() {
      _saving = true;
      _saveError = null;
    });
    try {
      await ref.read(backendConnectionProvider.notifier).clear();
      _loadedStoredSettings = false;
      _urlController.clear();
      _tokenController.clear();
    } on Exception catch (error) {
      if (mounted) setState(() => _saveError = error.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }
}

class _LinkStatus extends StatelessWidget {
  const _LinkStatus({
    required this.icon,
    required this.ready,
    required this.label,
    required this.value,
  });

  final IconData icon;
  final bool? ready;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final color = switch (ready) {
      true => TacticalColors.accent,
      false => TacticalColors.warning,
      null => TacticalColors.muted,
    };

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: color, size: 19),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 3),
                Text(
                  value,
                  style: const TextStyle(
                    color: TacticalColors.muted,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
