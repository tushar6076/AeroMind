import 'package:flutter/foundation.dart';

class DeviceInfoHelper {
  /// Returns a unique identifier key for the client type.
  static Future<String> getDeviceId() async {
    try {
      if (kIsWeb) {
        return 'web-client';
      }

      switch (defaultTargetPlatform) {
        case TargetPlatform.android:
          return 'android-app-client';
        case TargetPlatform.iOS:
          return 'ios-app-client';
        case TargetPlatform.macOS:
          return 'macos-desktop-client';
        case TargetPlatform.windows:
          return 'windows-desktop-client';
        case TargetPlatform.linux:
          return 'linux-desktop-client';
        case TargetPlatform.fuchsia:
          return 'fuchsia-client';
      }
    } catch (e) {
      debugPrint('Failed to retrieve device ID: $e');
    }

    return 'mobile-app-client';
  }

  /// Returns a clean, human-readable device platform string.
  static Future<String> getDeviceInfo() async {
    try {
      if (kIsWeb) {
        return 'Web Client';
      }

      switch (defaultTargetPlatform) {
        case TargetPlatform.android:
          return 'Android Client';
        case TargetPlatform.iOS:
          return 'iOS Client';
        case TargetPlatform.macOS:
          return 'macOS Client';
        case TargetPlatform.windows:
          return 'Windows Client';
        case TargetPlatform.linux:
          return 'Linux Client';
        case TargetPlatform.fuchsia:
          return 'Fuchsia Client';
      }
    } catch (e) {
      debugPrint('Failed to retrieve device info: $e');
    }

    return 'Mobile Application';
  }
}