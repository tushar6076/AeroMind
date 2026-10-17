import 'package:flutter/material.dart';

import 'color.dart';
import 'shapes.dart';

abstract final class TacticalTheme {
  static ThemeData get darkTheme {
    final colorScheme = ColorScheme.fromSeed(
      seedColor: TacticalColors.accent,
      brightness: Brightness.dark,
      surface: TacticalColors.surface,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: colorScheme.copyWith(
        primary: TacticalColors.accent,
        secondary: TacticalColors.blue,
        error: TacticalColors.danger,
        surface: TacticalColors.surface,
      ),
      scaffoldBackgroundColor: TacticalColors.background,
      canvasColor: TacticalColors.background,
      dividerColor: TacticalColors.outline,
      textTheme: ThemeData.dark().textTheme.apply(
        bodyColor: TacticalColors.text,
        displayColor: TacticalColors.text,
      ),
      cardTheme: const CardThemeData(
        color: TacticalColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: TacticalShapes.panelRadius,
          side: TacticalShapes.panelBorder,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          backgroundColor: TacticalColors.accent,
          foregroundColor: TacticalColors.background,
          shape: const RoundedRectangleBorder(
            borderRadius: TacticalShapes.buttonRadius,
          ),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
          textStyle: const TextStyle(fontWeight: FontWeight.w800),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: TacticalColors.text,
          side: const BorderSide(color: TacticalColors.outline),
          shape: const RoundedRectangleBorder(
            borderRadius: TacticalShapes.buttonRadius,
          ),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: TacticalColors.elevated,
        border: OutlineInputBorder(
          borderRadius: TacticalShapes.buttonRadius,
          borderSide: const BorderSide(color: TacticalColors.outline),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: TacticalShapes.buttonRadius,
          borderSide: const BorderSide(color: TacticalColors.outline),
        ),
      ),
    );
  }
}
