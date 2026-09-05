import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_strings.dart';
import '../../providers/api_provider.dart';
import '../../routes/app_routes.dart';
import '../../widgets/buttons/primary_button.dart';
import '../../widgets/common/app_scaffold.dart';
import '../../widgets/inputs/custom_textfield.dart';

class SignupScreen extends ConsumerStatefulWidget {
  const SignupScreen({super.key});

  @override
  ConsumerState<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends ConsumerState<SignupScreen> {
  int _currentStep = 1;

  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  final _step1Key = GlobalKey<FormState>();
  final _step2Key = GlobalKey<FormState>();

  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_step1Key.currentState?.validate() ?? false) {
      setState(() => _currentStep = 2);
    }
  }

  void _prevStep() {
    if (_currentStep == 2) {
      setState(() => _currentStep = 1);
    } else {
      Navigator.pop(context);
    }
  }

  Future<void> _handleSignup() async {
    if (!(_step2Key.currentState?.validate() ?? false)) return;

    setState(() => _isLoading = true);

    try {
      final apiService = ref.read(apiServiceProvider);
      final res = await apiService.register(
        _emailController.text.trim(),
        _passwordController.text,
        fullName: _nameController.text.trim(),
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
            content: Text('Account created successfully! Please log in.'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pushReplacementNamed(context, AppRoutes.login);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Registration failed: ${e.toString()}'),
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
      title: AppStrings.signupTitle,
      leading: IconButton(
        onPressed: _isLoading ? null : _prevStep,
        icon: const Icon(Icons.arrow_back_ios_new, size: 20, color: AppColors.textPrimary),
      ),
      actions: [
        Padding(
          padding: const EdgeInsets.only(right: 24.0),
          child: _buildStepDots(),
        ),
      ],
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              _currentStep == 1 ? 'Step 1: Basic Information' : 'Step 2: Security & Password',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.textSecondary,
                  ),
            ),
            const SizedBox(height: 20),

            // Animated Form Step
            Expanded(
              child: AnimatedSwitcher(
                duration: const Duration(milliseconds: 200),
                child: _currentStep == 1 ? _buildStep1() : _buildStep2(),
              ),
            ),

            // Bottom Action Button
            PrimaryButton(
              text: _currentStep == 1
                  ? 'Next'
                  : (_isLoading ? 'Registering...' : 'Register'),
              onPressed: _isLoading
                  ? () {}
                  : () {
                      if (_currentStep == 1) {
                        _nextStep();
                      } else {
                        _handleSignup();
                      }
                    },
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  Widget _buildStepDots() {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(2, (index) {
        final isActive = index + 1 == _currentStep;
        return AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          margin: const EdgeInsets.only(left: 6),
          height: 6,
          width: isActive ? 18 : 6,
          decoration: BoxDecoration(
            color: isActive ? AppColors.primary : AppColors.textSecondary.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(3),
          ),
        );
      }),
    );
  }

  Widget _buildStep1() {
    return SingleChildScrollView(
      child: Form(
        key: _step1Key,
        child: Column(
          key: const ValueKey(1),
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            CustomTextField(
              controller: _nameController,
              labelText: 'Full Name',
              prefixIcon: const Icon(Icons.person_outline, color: AppColors.textSecondary),
              validator: (val) => val == null || val.trim().isEmpty ? 'Please enter your name' : null,
            ),
            const SizedBox(height: 16),
            CustomTextField(
              controller: _emailController,
              labelText: 'Email',
              hintText: AppStrings.emailHint,
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
          ],
        ),
      ),
    );
  }

  Widget _buildStep2() {
    return SingleChildScrollView(
      child: Form(
        key: _step2Key,
        child: Column(
          key: const ValueKey(2),
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            CustomTextField(
              controller: _passwordController,
              labelText: 'Password',
              hintText: AppStrings.passwordHint,
              obscureText: true,
              prefixIcon: const Icon(Icons.lock_outline, color: AppColors.textSecondary),
              validator: (val) => val == null || val.length < 6 ? 'Password must be at least 6 characters' : null,
            ),
            const SizedBox(height: 16),
            CustomTextField(
              controller: _confirmPasswordController,
              labelText: 'Confirm Password',
              hintText: AppStrings.confirmPasswordHint,
              obscureText: true,
              prefixIcon: const Icon(Icons.lock_reset_outlined, color: AppColors.textSecondary),
              validator: (val) {
                if (val != _passwordController.text) {
                  return 'Passwords do not match';
                }
                return null;
              },
            ),
          ],
        ),
      ),
    );
  }
}