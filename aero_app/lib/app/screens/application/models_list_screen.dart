import 'package:flutter/material.dart' hide IconButton;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_riverpod/misc.dart';

import '../../core/constants/app_colors.dart';
import '../../models/ai_model.dart';
import '../../providers/ai_provider.dart';
import '../../routes/app_routes.dart';
import '../../widgets/buttons/icon_button.dart';
import '../../widgets/buttons/primary_button.dart';
import '../../widgets/cards/model_card.dart';
import '../../widgets/common/app_scaffold.dart';
import '../../widgets/common/loading_indicator.dart';
import '../../widgets/dialogs/confirm_dialog.dart';
import '../../widgets/inputs/search_field.dart';

class ModelsListScreen extends ConsumerStatefulWidget {
  const ModelsListScreen({super.key});

  @override
  ConsumerState<ModelsListScreen> createState() => _ModelsListScreenState();
}

class _ModelsListScreenState extends ConsumerState<ModelsListScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _searchController.addListener(_onSearchChanged);
  }

  void _onSearchChanged() {
    setState(() {
      _searchQuery = _searchController.text.trim().toLowerCase();
    });
  }

  @override
  void dispose() {
    _searchController.removeListener(_onSearchChanged);
    _searchController.dispose();
    _tabController.dispose();
    super.dispose();
  }

  List<AiModel> _filterModels(List<AiModel> models) {
    if (_searchQuery.isEmpty) return models;
    return models.where((model) {
      final nameMatches = model.name.toLowerCase().contains(_searchQuery);
      final idMatches = model.id.toLowerCase().contains(_searchQuery);
      final descMatches =
          model.description?.toLowerCase().contains(_searchQuery) ?? false;
      return nameMatches || idMatches || descMatches;
    }).toList();
  }

  Future<void> _handleRevokeAll() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => ConfirmDialog(
        title: 'Revoke All Models',
        message:
            'This action will revoke API keys for ALL deployed models. Are you sure you want to proceed?',
        confirmText: 'Revoke All',
        onConfirm: () => Navigator.of(dialogContext).pop(true),
      ),
    );

    if (confirmed != true) return;

    final success = await ref
        .read(aiModelManagerProvider.notifier)
        .revokeAllModels();

    if (!mounted) return;

    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('All model keys have been revoked successfully.'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      final state = ref.read(aiModelManagerProvider);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            state.error?.toString() ?? 'Failed to revoke all model keys.',
          ),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final managerState = ref.watch(aiModelManagerProvider);

    final activeModelsAsync = ref.watch(activeAiModelsProvider);
    final inPlayModelsAsync = ref.watch(inPlayAiModelsProvider);

    return AppScaffold(
      showAppBar: true,
      title: 'AI Models',
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 12.0),
          child: AppIconButton(
            icon: Icons.published_with_changes_outlined,
            color: Colors.redAccent,
            onPressed: () {
              if (!managerState.isLoading) {
                _handleRevokeAll();
              }
            },
          ),
        ),
      ],
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Search Field Widget
              SearchField(
                controller: _searchController,
                hintText: 'Search models by name or key...',
              ),
              const SizedBox(height: 16),

              // Custom Tab Controls Bar
              Container(
                height: 44,
                padding: const EdgeInsets.all(4),
                decoration: BoxDecoration(
                  color: AppColors.textSecondary.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: TabBar(
                  controller: _tabController,
                  indicator: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  labelColor: Colors.white,
                  unselectedLabelColor: AppColors.textSecondary,
                  indicatorSize: TabBarIndicatorSize.tab,
                  dividerColor: Colors.transparent,
                  tabs: const [
                    Tab(text: 'Active Models'),
                    Tab(text: 'In-Play / All'),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Main Tab Content View
              Expanded(
                child: managerState.isLoading
                    ? const Center(child: LoadingIndicator())
                    : TabBarView(
                        controller: _tabController,
                        children: [
                          _buildModelList(
                            asyncVal: activeModelsAsync,
                            emptyMessage: 'No active AI models found.',
                            providerToInvalidate: activeAiModelsProvider,
                          ),
                          _buildModelList(
                            asyncVal: inPlayModelsAsync,
                            emptyMessage: 'No in-play models configured.',
                            providerToInvalidate: inPlayAiModelsProvider,
                          ),
                        ],
                      ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildModelList({
    required AsyncValue<List<AiModel>> asyncVal,
    required String emptyMessage,
    required ProviderOrFamily providerToInvalidate,
  }) {
    return asyncVal.when(
      data: (models) {
        final filteredList = _filterModels(models);

        if (filteredList.isEmpty) {
          return Center(
            child: Text(
              _searchQuery.isNotEmpty
                  ? 'No models matching "$_searchQuery"'
                  : emptyMessage,
              style: const TextStyle(
                color: AppColors.textSecondary,
                fontSize: 14,
              ),
            ),
          );
        }

        return RefreshIndicator(
          color: AppColors.primary,
          onRefresh: () async {
            ref.invalidate(providerToInvalidate);
          },
          child: ListView.separated(
            padding: const EdgeInsets.symmetric(vertical: 4.0),
            itemCount: filteredList.length,
            separatorBuilder: (_, _) => const SizedBox(height: 12),
            itemBuilder: (context, index) {
              final model = filteredList[index];
              return ModelCard(
                modelName: model.name,
                description: model.description ?? 'No description available',
                version: 'v1.0',
                isActive: model.isActive,
                onTap: () {
                  Navigator.pushNamed(
                    context,
                    AppRoutes.modelInfo,
                    arguments: model,
                  );
                },
              );
            },
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
              const Icon(Icons.error_outline, color: Colors.redAccent, size: 40),
              const SizedBox(height: 12),
              Text(
                'Error loading models:\n$err',
                textAlign: TextAlign.center,
                style: const TextStyle(color: AppColors.textSecondary, fontSize: 13),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: 140,
                child: PrimaryButton(
                  text: 'Retry',
                  onPressed: () => ref.invalidate(providerToInvalidate),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}