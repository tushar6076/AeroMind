import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_strings.dart';
import '../../providers/api_provider.dart';
import '../../routes/app_routes.dart';
import '../../widgets/buttons/primary_button.dart';
import '../../widgets/common/app_scaffold.dart';
import '../../widgets/inputs/custom_textfield.dart';

class ResetPasswordScreen extends ConsumerStatefulWidget {
  const ResetPasswordScreen({super.key});

  @override
  ConsumerState<ResetPasswordScreen> createState() => _ResetPasswordScreenState();
}

class _ResetPasswordScreenState extends ConsumerState<ResetPasswordScreen> {
  final _codeController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  @override
  void dispose() {
    _codeController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  Future<void> _confirmReset() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;

    setState(() => _isLoading = true);

    // Retrieve passed email from route arguments
    final email = ModalRoute.of(context)?.settings.arguments as String? ?? '';

    try {
      final apiService = ref.read(apiServiceProvider);
      final res = await apiService.resetPassword(
        email: email,
        code: _codeController.text.trim(),
        newPassword: _newPasswordController.text,
      );

      if (!mounted) return;

      if (res.containsKey('detail')) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(res['detail'].toString()),
            backgroundColor: Theme.of(context).colorScheme.error,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Password reset successfully! Please log in.'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pushNamedAndRemoveUntil(context, AppRoutes.login, (route) => false);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Reset failed: ${e.toString()}'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppScaffold(
      title: 'Reset Password',
      leading: IconButton(
        onPressed: _isLoading ? null : () => Navigator.pop(context),
        icon: const Icon(Icons.arrow_back_ios_new, size: 20, color: AppColors.textPrimary),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'Enter the verification code sent to your email along with your new password.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
              const SizedBox(height: 24),
              CustomTextField(
                controller: _codeController,
                labelText: 'Reset Code',
                keyboardType: TextInputType.number,
                prefixIcon: const Icon(Icons.pin_outlined, color: AppColors.textSecondary),
                validator: (val) => val == null || val.trim().isEmpty ? 'Enter reset code' : null,
              ),
              const SizedBox(height: 16),
              CustomTextField(
                controller: _newPasswordController,
                labelText: 'New Password',
                hintText: AppStrings.passwordHint,
                obscureText: true,
                prefixIcon: const Icon(Icons.lock_outline, color: AppColors.textSecondary),
                validator: (val) => val == null || val.length < 6 ? 'Password must be at least 6 characters' : null,
              ),
              const SizedBox(height: 16),
              CustomTextField(
                controller: _confirmPasswordController,
                labelText: 'Confirm New Password',
                hintText: AppStrings.confirmPasswordHint,
                obscureText: true,
                prefixIcon: const Icon(Icons.lock_reset_outlined, color: AppColors.textSecondary),
                validator: (val) {
                  if (val != _newPasswordController.text) {
                    return 'Passwords do not match';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 32),
              PrimaryButton(
                text: _isLoading ? 'Updating...' : 'Update Password',
                onPressed: _isLoading ? () {} : _confirmReset,
              ),
            ],
          ),
        ),
      ),
    );
  }
}