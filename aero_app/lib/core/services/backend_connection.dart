import 'dart:convert';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../constants/default_configs.dart';
import 'connection_store.dart';

class BackendConnection {
  const BackendConnection({required this.baseUri, required this.accessToken});

  final Uri baseUri;
  final String? accessToken;

  factory BackendConnection.fromJson(Map<String, dynamic> json) {
    final rawUrl = json['url'];
    final rawToken = json['token'];
    if (rawUrl is! String || (rawToken != null && rawToken is! String)) {
      throw const FormatException('Saved backend connection is invalid.');
    }
    return BackendConnection(
      baseUri: _parseBaseUri(rawUrl),
      accessToken: rawToken as String?,
    );
  }
}

Uri _parseBaseUri(String value) {
  final uri = Uri.tryParse(value.trim());
  if (uri == null ||
      !const {'http', 'https'}.contains(uri.scheme) ||
      uri.host.isEmpty ||
      uri.userInfo.isNotEmpty ||
      uri.hasQuery ||
      uri.hasFragment) {
    throw const FormatException('Enter a valid HTTP or HTTPS backend URL.');
  }
  return uri;
}

class BackendConnectionController extends AsyncNotifier<BackendConnection?> {
  static const _storageKey = 'aeromind.backend.connection';

  @override
  Future<BackendConnection?> build() async {
    const environmentUrl = DefaultConfigs.backendUrl;
    if (environmentUrl.isNotEmpty) {
      return BackendConnection(
        baseUri: _parseBaseUri(environmentUrl),
        accessToken: DefaultConfigs.apiAccessToken.isEmpty
            ? null
            : DefaultConfigs.apiAccessToken,
      );
    }
    final stored = await ref.read(connectionStoreProvider).read(_storageKey);
    if (stored == null) return null;
    final decoded = jsonDecode(stored);
    if (decoded is! Map) {
      throw const FormatException('Saved backend connection is invalid.');
    }
    return BackendConnection.fromJson(Map<String, dynamic>.from(decoded));
  }

  Future<void> configure({
    required String url,
    required String accessToken,
  }) async {
    final parsed = BackendConnection(
      baseUri: _parseBaseUri(url),
      accessToken: accessToken.trim().isEmpty ? null : accessToken.trim(),
    );
    final encoded = jsonEncode({
      'url': parsed.baseUri.toString(),
      'token': parsed.accessToken,
    });
    await ref.read(connectionStoreProvider).write(_storageKey, encoded);
    state = AsyncData(parsed);
  }

  Future<void> clear() async {
    await ref.read(connectionStoreProvider).delete(_storageKey);
    state = const AsyncData(null);
  }
}

final backendConnectionProvider =
    AsyncNotifierProvider<BackendConnectionController, BackendConnection?>(
      BackendConnectionController.new,
    );
