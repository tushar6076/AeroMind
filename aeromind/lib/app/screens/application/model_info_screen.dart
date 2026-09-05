import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/constants/app_colors.dart';
import '../../models/ai_model.dart';
import '../../providers/ai_provider.dart';
import '../../widgets/buttons/icon_button.dart';
import '../../widgets/buttons/primary_button.dart';
import '../../widgets/common/app_scaffold.dart';
import '../../widgets/dialogs/confirm_dialog.dart';

class ModelInfoScreen extends ConsumerWidget {
  const ModelInfoScreen({super.key});

  Future<void> _handleRevokeModel(
    BuildContext context,
    WidgetRef ref,
    AiModel model,
  ) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => ConfirmDialog(
        title: 'Revoke Key',
        message:
            'Are you sure you want to revoke the key for ${model.name}? This model will no longer process requests.',
        confirmText: 'Revoke',
        onConfirm: () => Navigator.of(dialogContext).pop(true),
      ),
    );

    if (confirmed != true) return;

    final success = await ref
        .read(aiModelManagerProvider.notifier)
        .revokeAllModels();

    if (!context.mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${model.name} key revoked successfully.'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.of(context).pop();
    } else {
      final state = ref.read(aiModelManagerProvider);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            state.error?.toString() ?? 'Failed to revoke model key.',
          ),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final model = ModalRoute.of(context)?.settings.arguments as AiModel?;

    if (model == null) {
      return AppScaffold(
        showAppBar: true,
        title: 'Model Details',
        body: const Center(
          child: Text(
            'No model details found.',
            style: TextStyle(color: AppColors.textSecondary),
          ),
        ),
      );
    }

    return AppScaffold(
      showAppBar: true,
      title: model.name,
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 12.0),
          child: AppIconButton(
            icon: Icons.key_off_outlined,
            color: Colors.redAccent,
            onPressed: () => _handleRevokeModel(context, ref, model),
          ),
        ),
      ],
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Status Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.textSecondary.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: AppColors.textSecondary.withValues(alpha: 0.12),
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.primary.withValues(alpha: 0.15),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.memory_outlined,
                        color: AppColors.primary,
                        size: 28,
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            model.name,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            'ID: ${model.id}',
                            style: const TextStyle(
                              fontSize: 12,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 10,
                        vertical: 4,
                      ),
                      decoration: BoxDecoration(
                        color: model.isActive
                            ? Colors.green.withValues(alpha: 0.15)
                            : Colors.orange.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        model.isActive ? 'Active' : 'Inactive',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: model.isActive ? Colors.green : Colors.orange,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Description
              if (model.description != null && model.description!.isNotEmpty) ...[
                const Text(
                  'Overview',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  model.description!,
                  style: const TextStyle(
                    fontSize: 14,
                    color: AppColors.textSecondary,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 24),
              ],

              // Technical Specifications Grid
              const Text(
                'Specifications',
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
                childAspectRatio: 2.2,
                crossAxisSpacing: 12,
                mainAxisSpacing: 12,
                children: [
                  _buildSpecTile(
                    label: 'Status',
                    value: model.isActive ? 'Active' : 'Inactive',
                    icon: Icons.hub_outlined,
                  ),
                  _buildSpecTile(
                    label: 'Context Window',
                    value: '128k tokens',
                    icon: Icons.data_array_outlined,
                  ),
                  _buildSpecTile(
                    label: 'Latency Target',
                    value: '120 ms',
                    icon: Icons.speed_outlined,
                  ),
                  _buildSpecTile(
                    label: 'Cost / 1k Tokens',
                    value: '\$0.002',
                    icon: Icons.attach_money_outlined,
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // Performance & Benchmarks Section
              const Text(
                'Performance & Benchmarks',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                ),
              ),
              const SizedBox(height: 12),
              _buildBenchmarkBar('MMLU Reasoning', 0.84),
              const SizedBox(height: 12),
              _buildBenchmarkBar('HumanEval Code', 0.78),
              const SizedBox(height: 12),
              _buildBenchmarkBar('GSM8K Math', 0.88),

              const SizedBox(height: 32),

              // Danger Zone Action
              PrimaryButton(
                text: 'Revoke Key',
                backgroundColor: Colors.redAccent.withValues(alpha: 0.15),
                onPressed: () => _handleRevokeModel(context, ref, model),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSpecTile({
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

  Widget _buildBenchmarkBar(String label, double score) {
    final percentage = (score * 100).clamp(0, 100).toInt();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: const TextStyle(
                fontSize: 13,
                color: AppColors.textSecondary,
              ),
            ),
            Text(
              '$percentage%',
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: score,
            minHeight: 6,
            backgroundColor: AppColors.textSecondary.withValues(alpha: 0.1),
            valueColor: const AlwaysStoppedAnimation<Color>(AppColors.primary),
          ),
        ),
      ],
    );
  }
}