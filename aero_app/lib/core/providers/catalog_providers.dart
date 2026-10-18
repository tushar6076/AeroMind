import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/backend_catalog.dart';
import '../network/http_client.dart';

final aiInventoryProvider = FutureProvider.autoDispose<AiInventory>((ref) {
  return ref.watch(aeroCloudClientProvider).getAiInventory();
});

final vaultInventoryProvider = FutureProvider.autoDispose<VaultInventory>((
  ref,
) {
  return ref.watch(aeroCloudClientProvider).getVaultInventory();
});
