import 'package:flutter/material.dart';
import '../screens/splash/splash_screen.dart';
import '../screens/auth/login_screen.dart';
import '../screens/auth/signup_screen.dart';
import '../screens/auth/forgot_password_screen.dart';
import '../screens/auth/reset_password_screen.dart';
import '../screens/home/home_screen.dart';
import '../screens/controller/controller_screen.dart';
import '../screens/flight/flight_info_screen.dart';
import '../screens/application/models_list_screen.dart';
import '../screens/application/model_info_screen.dart';
import '../screens/application/model_implement_screen.dart';
import '../screens/admin/overview_page.dart';
import '../screens/admin/active_users_page.dart';
import '../screens/admin/control_page.dart';
import '../screens/admin/ai_application_page.dart';
import '../screens/settings/settings_layout.dart';

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String forgotPassword = '/forgot-password';
  static const String resetPassword = '/reset-password';
  static const String home = '/home';
  static const String controller = '/controller';
  static const String flightInfo = '/flight-info';
  static const String modelsList = '/models-list';
  static const String aiModelsList = '/models-list'; // Alias route getter
  static const String modelInfo = '/model-info';
  static const String modelImplement = '/model-implement';
  static const String adminOverview = '/admin/overview';
  static const String adminActiveUsers = '/admin/active-users';
  static const String adminControl = '/admin/control';
  static const String adminAiApplication = '/admin/ai-application';
  static const String adminAiManagement = '/admin/ai-application'; // Alias route getter
  static const String settingsOverview = '/settings/overview';
  static const String settingsEditProfile = '/settings/edit-profile';
  static const String settingsChangePassword = '/settings/change-password';
  static const String settingsPreferences = '/settings/preferences';
  static const String settingsFlightHistory = '/settings/flight-history';
  static const String settingsDeleteAccount = '/settings/delete-account';

  static Map<String, WidgetBuilder> getRoutes() {
    return {
      splash: (context) => const SplashScreen(),
      login: (context) => const LoginScreen(),
      signup: (context) => const SignupScreen(),
      forgotPassword: (context) => const ForgotPasswordScreen(),
      resetPassword: (context) => const ResetPasswordScreen(),
      home: (context) => const HomeScreen(),
      controller: (context) => const ControllerScreen(),
      flightInfo: (context) => const FlightInfoScreen(),
      modelsList: (context) => const ModelsListScreen(),
      modelInfo: (context) => const ModelInfoScreen(),
      modelImplement: (context) => const ModelImplementScreen(),
      adminOverview: (context) => const AdminOverviewPage(),
      adminActiveUsers: (context) => const ActiveUsersPage(),
      adminControl: (context) => const ControlPage(),
      adminAiApplication: (context) => const AiApplicationPage(),
      settingsOverview: (context) => const SettingsLayout(initialIndex: 0),
      settingsEditProfile: (context) => const SettingsLayout(initialIndex: 1),
      settingsChangePassword: (context) => const SettingsLayout(initialIndex: 2),
      settingsPreferences: (context) => const SettingsLayout(initialIndex: 3),
      settingsFlightHistory: (context) => const SettingsLayout(initialIndex: 4),
    };
  }
}