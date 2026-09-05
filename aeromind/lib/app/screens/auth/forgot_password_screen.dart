import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/app_colors.dart';
import '../../providers/api_provider.dart';
import '../../routes/app_routes.dart';
import '../../widgets/buttons/primary_button.dart';
import '../../widgets/common/app_scaffold.dart';
import '../../widgets/inputs/custom_textfield.dart';

class ForgotPasswordScreen extends ConsumerStatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  ConsumerState<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends ConsumerState<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _handleResetRequest() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;

    setState(() => _isLoading = true);

    try {
      final apiService = ref.read(apiServiceProvider);
      final email = _emailController.text.trim();

      // Trigger forgot password API endpoint
      final res = await apiService.requestPasswordReset(email);

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
            content: Text('Reset code sent to your email address.'),
            backgroundColor: Colors.green,
          ),
        );
        // Pass email address as argument to reset password screen
        Navigator.pushNamed(
          context,
          AppRoutes.resetPassword,
          arguments: email,
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error: ${e.toString()}'),
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
      title: 'Forgot Password',
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
                'Enter your registered email address to receive password reset instructions.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: AppColors.textSecondary,
                    ),
              ),
              const SizedBox(height: 24),
              CustomTextField(
                controller: _emailController,
                labelText: 'Email Address',
                keyboardType: TextInputType.emailAddress,
                prefixIcon: const Icon(Icons.email_outlined, color: AppColors.textSecondary),
                validator: (val) {
                  if (val == null || val.trim().isEmpty) return 'Please enter email';
                  if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(val.trim())) {
                    return 'Please enter a valid email address';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 32),
              PrimaryButton(
                text: _isLoading ? 'Sending...' : 'Send Code',
                onPressed: _isLoading ? () {} : _handleResetRequest,
              ),
            ],
          ),
        ),
      ),
    );
  }
}