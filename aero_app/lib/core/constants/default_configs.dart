abstract final class DefaultConfigs {
  static const backendUrl = String.fromEnvironment('AERO_CLOUD_URL');
  static const apiAccessToken = String.fromEnvironment('AERO_API_TOKEN');
  static const requestTimeout = Duration(seconds: 5);
  static const statusRefreshInterval = Duration(seconds: 3);
}
