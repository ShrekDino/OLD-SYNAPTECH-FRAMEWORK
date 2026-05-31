import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'app_colors.dart';

abstract final class SamChatTheme {
  SamChatTheme._();

  static ThemeData dark(Color accent) => ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: SamChatColors.background,
        colorScheme: ColorScheme.dark(
          primary: accent,
          secondary: SamChatColors.accentUrgent,
          surface: SamChatColors.surface,
          onSurface: SamChatColors.onSurface,
        ),
        appBarTheme: AppBarTheme(
          backgroundColor: SamChatColors.surfaceElevated,
          foregroundColor: SamChatColors.onSurface,
          elevation: 0,
          scrolledUnderElevation: 0.5,
          centerTitle: true,
          titleTextStyle: const TextStyle(
            color: SamChatColors.onSurface,
            fontSize: 17,
            fontWeight: FontWeight.w600,
          ),
        ),
        bottomNavigationBarTheme: const BottomNavigationBarThemeData(
          backgroundColor: SamChatColors.surfaceElevated,
          selectedItemColor: SamChatColors.accentSilent,
          unselectedItemColor: SamChatColors.onSurfaceDim,
          elevation: 0,
        ),
        dividerTheme: const DividerThemeData(
          color: SamChatColors.divider,
          thickness: 0.5,
        ),
        snackBarTheme: SnackBarThemeData(
          backgroundColor: SamChatColors.snackbarDefault,
          contentTextStyle: const TextStyle(
            color: SamChatColors.onSurface,
            fontSize: 14,
          ),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: SamChatColors.inputBackground,
          border: const OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(20)),
            borderSide: BorderSide.none,
          ),
          enabledBorder: const OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(20)),
            borderSide: BorderSide(color: SamChatColors.inputBorder, width: 1),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: const BorderRadius.all(Radius.circular(20)),
            borderSide: BorderSide(color: accent, width: 1),
          ),
          hintStyle: const TextStyle(
            color: SamChatColors.onSurfaceDisabled,
            fontSize: 16,
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        ),
        textSelectionTheme: TextSelectionThemeData(
          cursorColor: accent,
          selectionColor: accent.withValues(alpha: 0.3),
          selectionHandleColor: accent,
        ),
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: {
            TargetPlatform.android: CupertinoPageTransitionsBuilder(),
            TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
          },
        ),
      );

  static ThemeData light(Color accent) => ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF2F2F7),
        colorScheme: ColorScheme.light(
          primary: accent,
          secondary: SamChatColors.accentUrgent,
          surface: Colors.white,
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Color(0xFF1C1C1E),
          elevation: 0,
          scrolledUnderElevation: 0.5,
          centerTitle: true,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFFE5E5EA),
          border: const OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(20)),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: const BorderRadius.all(Radius.circular(20)),
            borderSide: BorderSide(color: accent.withValues(alpha: 0.3)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: const BorderRadius.all(Radius.circular(20)),
            borderSide: BorderSide(color: accent, width: 2),
          ),
          hintStyle: const TextStyle(
            color: Color(0xFF8E8E93),
            fontSize: 16,
          ),
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        ),
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: {
            TargetPlatform.android: CupertinoPageTransitionsBuilder(),
            TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
          },
        ),
      );
}
