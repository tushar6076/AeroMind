import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/constants/api_endpoints.dart';
import '../../core/constants/app_colors.dart';
import '../../core/services/api_service.dart';
import '../../providers/auth_provider.dart';
import '../../providers/telemetry_provider.dart';
import '../../widgets/buttons/icon_button.dart';
import '../../widgets/buttons/primary_button.dart';
import '../../widgets/common/app_scaffold.dart';
import '../../widgets/common/loading_indicator.dart';
import '../../widgets/dialogs/confirm_dialog.dart';

class FlightInfoScreen extends ConsumerStatefulWidget {
  const FlightInfoScreen({super.key});

  @override
  ConsumerState<FlightInfoScreen> createState() => _FlightInfoScreenState();
}

class _FlightInfoScreenState extends ConsumerState<FlightInfoScreen> {
  bool _isExecutingCommand = false;

  Future<void> _sendCommand(
    String endpoint,
    String actionName, {
    Map<String, dynamic>? payload,
    bool requiresConfirmation = false,
  }) async {
    if (_isExecutingCommand) return;

    if (requiresConfirmation) {
      final confirm = await showDialog<bool>(
        context: context,
        builder: (dialogContext) => ConfirmDialog(
          title: 'Confirm Action',
          message: 'Are you sure you want to execute $actionName?',
          confirmText: 'Execute',
          onConfirm: () => Navigator.of(dialogContext).pop(true),
        ),
      );
      if (confirm != true) return;
    }

    setState(() {
      _isExecutingCommand = true;
    });

    try {
      final authState = ref.read(authProvider);
      final apiService = ApiService();
      if (authState.token != null) {
        apiService.setToken(authState.token!);
      }

      final success = await apiService.sendFlightCommand(
        endpoint,
        payload: payload,
      );

      if (!mounted) return;

      if (success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$actionName command sent successfully.'),
            backgroundColor: Colors.green,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to execute $actionName.'),
            backgroundColor: Colors.redAccent,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: ${e.toString()}'),
          backgroundColor: Colors.redAccent,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isExecutingCommand = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    const clientId = 'mobile-client-flight';
    final telemetryAsync = ref.watch(telemetryStreamProvider(clientId));

    return AppScaffold(
      showAppBar: true,
      title: 'Flight Information',
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 12.0),
          child: AppIconButton(
            icon: Icons.refresh_outlined,
            color: AppColors.primary,
            onPressed: () {
              ref.invalidate(telemetryStreamProvider(clientId));
            },
          ),
        ),
      ],
      body: SafeArea(
        child: telemetryAsync.when(
          data: (rawStreamData) {
            final Map<String, dynamic> data = _parseStreamData(rawStreamData);

            final double altitude = (data['altitude'] ?? 0.0).toDouble();
            final double speed = (data['speed'] ?? 0.0).toDouble();
            final int battery = (data['battery'] ?? 0).toInt();
            final double lat = (data['latitude'] ?? 0.0).toDouble();
            final double lng = (data['longitude'] ?? 0.0).toDouble();
            final double pitch = (data['pitch'] ?? 0.0).toDouble();
            final double roll = (data['roll'] ?? 0.0).toDouble();
            final int signal = (data['signal_strength'] ?? 100).toInt();
            final String flightMode = data['mode']?.toString() ?? 'STABILIZE';

            return SingleChildScrollView(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // System Status Card
                  _buildStatusCard(
                    flightMode: flightMode,
                    battery: battery,
                    signal: signal,
                  ),
                  const SizedBox(height: 20),

                  // Telemetry Grid
                  const Text(
                    'Live Metrics',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 12),
                  GridView.count(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    crossAxisCount: 2,
                    childAspectRatio: 2.1,
                    crossAxisSpacing: 12,
                    mainAxisSpacing: 12,
                    children: [
                      _buildMetricTile(
                        label: 'Altitude',
                        value: '${altitude.toStringAsFixed(1)} m',
                        icon: Icons.height_outlined,
                      ),
                      _buildMetricTile(
                        label: 'Speed',
                        value: '${speed.toStringAsFixed(1)} m/s',
                        icon: Icons.speed_outlined,
                      ),
                      _buildMetricTile(
                        label: 'Pitch / Roll',
                        value: '${pitch.toStringAsFixed(1)}° / ${roll.toStringAsFixed(1)}°',
                        icon: Icons.screen_rotation_outlined,
                      ),
                      _buildMetricTile(
                        label: 'Coordinates',
                        value: '${lat.toStringAsFixed(4)}, ${lng.toStringAsFixed(4)}',
                        icon: Icons.location_on_outlined,
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Flight Control Commands
                  const Text(
                    'Flight Controls',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: PrimaryButton(
                          text: 'Takeoff',
                          onPressed: _isExecutingCommand
                              ? () {}
                              : () => _sendCommand(
                                    ApiEndpoints.takeoff,
                                    'Takeoff',
                                    payload: {'altitude': 5.0},
                                  ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: PrimaryButton(
                          text: 'Land',
                          backgroundColor: Colors.amber.withValues(alpha: 0.2),
                          onPressed: _isExecutingCommand
                              ? () {}
                              : () => _sendCommand(
                                    ApiEndpoints.land,
                                    'Landing',
                                  ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: PrimaryButton(
                          text: 'RTL (Return to Launch)',
                          backgroundColor: AppColors.primary.withValues(alpha: 0.2),
                          onPressed: _isExecutingCommand
                              ? () {}
                              : () => _sendCommand(
                                    ApiEndpoints.rtl,
                                    'Return to Launch',
                                  ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  PrimaryButton(
                    text: 'EMERGENCY STOP',
                    backgroundColor: Colors.redAccent.withValues(alpha: 0.2),
                    onPressed: _isExecutingCommand
                        ? () {}
                        : () => _sendCommand(
                              ApiEndpoints.emergencyStop,
                              'Emergency Stop',
                              requiresConfirmation: true,
                            ),
                  ),
                ],
              ),
            );
          },
          loading: () => const Center(child: LoadingIndicator()),
          error: (err, stack) => Center(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.wifi_off_outlined,
                    color: Colors.redAccent,
                    size: 40,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Telemetry stream disconnected:\n$err',
                    textAlign: TextAlign.center,
                    style: const TextStyle(
                      color: AppColors.textSecondary,
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: 140,
                    child: PrimaryButton(
                      text: 'Reconnect',
                      onPressed: () {
                        ref.invalidate(telemetryStreamProvider(clientId));
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Map<String, dynamic> _parseStreamData(dynamic rawData) {
    if (rawData is Map<String, dynamic>) {
      return rawData;
    }
    if (rawData is String) {
      try {
        return jsonDecode(rawData) as Map<String, dynamic>;
      } catch (_) {}
    }
    return {};
  }

  Widget _buildStatusCard({
    required String flightMode,
    required int battery,
    required int signal,
  }) {
    final batteryColor = battery > 50
        ? Colors.green
        : (battery > 20 ? Colors.orange : Colors.redAccent);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.textSecondary.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: AppColors.textSecondary.withValues(alpha: 0.12),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: const Icon(
                  Icons.flight_takeoff_outlined,
                  color: AppColors.primary,
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    flightMode,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Row(
                    children: [
                      const Icon(
                        Icons.wifi,
                        size: 14,
                        color: AppColors.textSecondary,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        'Signal: $signal%',
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: batteryColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.battery_charging_full_outlined,
                  size: 16,
                  color: batteryColor,
                ),
                const SizedBox(width: 4),
                Text(
                  '$battery%',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: batteryColor,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetricTile({
    required String label,
    required String value,
    required IconData icon,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.textSecondary.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(
          color: AppColors.textSecondary.withValues(alpha: 0.08),
        ),
      ),
      child: Row(
        children: [
          Icon(icon, color: AppColors.primary, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 11,
                    color: AppColors.textSecondary,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}