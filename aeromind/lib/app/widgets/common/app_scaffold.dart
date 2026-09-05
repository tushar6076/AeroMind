import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class AppScaffold extends StatelessWidget {
  /// Can pass either a [String] or a custom [Widget] as title.
  final dynamic title;
  final TextStyle? titleTextStyle;
  final Widget body;
  final Widget? leading;
  final List<Widget>? actions;
  final PreferredSizeWidget? bottom;
  final Widget? drawer;
  final Widget? floatingActionButton;
  final bool showAppBar;
  final bool centerTitle;
  final double elevation;
  final Color? backgroundColor;

  const AppScaffold({
    super.key,
    this.title,
    this.titleTextStyle,
    required this.body,
    this.leading,
    this.actions,
    this.bottom,
    this.drawer,
    this.floatingActionButton,
    this.showAppBar = true,
    this.centerTitle = false,
    this.elevation = 0,
    this.backgroundColor,
  });

  Widget? _buildTitle(BuildContext context) {
    if (title == null) return null;
    if (title is Widget) return title as Widget;
    if (title is String) {
      return Text(
        title as String,
        style: titleTextStyle ??
            Theme.of(context).textTheme.titleLarge?.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.bold,
                ),
      );
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor ?? AppColors.background,
      appBar: showAppBar && (title != null || leading != null || actions != null)
          ? AppBar(
              title: _buildTitle(context),
              leading: leading,
              actions: actions,
              bottom: bottom,
              centerTitle: centerTitle,
              elevation: elevation,
              backgroundColor: Colors.transparent,
              surfaceTintColor: Colors.transparent,
            )
          : null,
      drawer: drawer,
      body: SafeArea(child: body),
      floatingActionButton: floatingActionButton,
    );
  }
}