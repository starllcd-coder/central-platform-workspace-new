import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppColors {
  static const Color primary = Color(0xFF1E6CCB);
  static const Color primaryDark = Color(0xFF134B8A);
  static const Color primaryDeep = Color(0xFF0B2A52);
  static const Color primarySoft = Color(0xFFEAF2FF);
  static const Color secondary = Color(0xFFF6FAFF);
  static const Color accent = Color(0xFF19B6B6);
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFFFB020);
  static const Color info = Color(0xFF00B8D9);
  static const Color background = Color(0xFFF6FAFF);
  static const Color darkBackground = Color(0xFF0E1424);
  static const Color card = Color(0xFFFFFFFF);
  static const Color textPrimary = Color(0xFF1F2A37);
  static const Color textMuted = Color(0xFF7B8BA3);
  static const Color border = Color(0xFFE6EEF9);
}

class AppTheme {
  static ThemeData get lightTheme => _theme(Brightness.light);
  static ThemeData get darkTheme => _theme(Brightness.dark);

  static TextTheme textThemeForLocale(String languageCode) {
    final code = languageCode.toLowerCase();
    final base = code.startsWith('ar')
        ? GoogleFonts.cairoTextTheme()
        : GoogleFonts.plusJakartaSansTextTheme();
    return base.apply(
      bodyColor: AppColors.textPrimary,
      displayColor: AppColors.textPrimary,
    );
  }

  static ThemeData _theme(Brightness brightness) {
    final bool dark = brightness == Brightness.dark;
    final ColorScheme scheme = ColorScheme.fromSeed(
      seedColor: AppColors.primary,
      brightness: brightness,
    );
    final baseText = textThemeForLocale('en');
    return ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: scheme,
      scaffoldBackgroundColor:
          dark ? AppColors.darkBackground : AppColors.background,
      textTheme: baseText.copyWith(
        headlineMedium: baseText.headlineMedium
            ?.copyWith(fontSize: 28, fontWeight: FontWeight.w800, height: 1.1),
        titleLarge: baseText.titleLarge
            ?.copyWith(fontSize: 20, fontWeight: FontWeight.w800, height: 1.2),
        titleMedium: baseText.titleMedium
            ?.copyWith(fontSize: 16, fontWeight: FontWeight.w700, height: 1.25),
        bodyLarge: baseText.bodyLarge?.copyWith(
            fontSize: 15,
            fontWeight: FontWeight.w500,
            height: 1.4,
            color: AppColors.textMuted),
        bodyMedium: baseText.bodyMedium?.copyWith(
            fontSize: 14,
            fontWeight: FontWeight.w400,
            height: 1.45,
            color: AppColors.textMuted),
      ),
      fontFamilyFallback: const ['Cairo'],
      appBarTheme: AppBarTheme(
        centerTitle: false,
        backgroundColor: Colors.transparent,
        foregroundColor: dark ? Colors.white : AppColors.textPrimary,
        elevation: 0,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: dark ? const Color(0xFF111A2D) : Colors.white,
        indicatorColor: dark ? AppColors.primaryDark : AppColors.primaryDark,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return TextStyle(
            fontWeight: selected ? FontWeight.w800 : FontWeight.w600,
            fontSize: 12,
            color: selected ? Colors.white : AppColors.textMuted,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return IconThemeData(
            color: selected ? Colors.white : AppColors.textMuted,
            size: 24,
          );
        }),
      ),
      cardTheme: CardThemeData(
        color: dark ? const Color(0xFF172033) : Colors.white,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        elevation: 0,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primaryDark,
          foregroundColor: Colors.white,
          // Do not force infinite width globally; it breaks buttons inside Row/Flex.
          minimumSize: const Size(0, 50),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
          elevation: 0,
        ).copyWith(
          backgroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.pressed)) return AppColors.primaryDeep;
            if (states.contains(WidgetState.disabled)) {
              return AppColors.primaryDark.withValues(alpha: 0.55);
            }
            return AppColors.primaryDark;
          }),
          overlayColor: WidgetStateProperty.all(AppColors.primaryDeep.withValues(alpha: 0.12)),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primaryDark,
          // Keep height consistent without forcing full-width in constrained layouts.
          minimumSize: const Size(0, 50),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
          side: const BorderSide(color: AppColors.border),
          backgroundColor: Colors.white,
          textStyle: const TextStyle(fontWeight: FontWeight.w800, fontSize: 15),
        ).copyWith(
          overlayColor:
              WidgetStateProperty.all(AppColors.primary.withValues(alpha: 0.06)),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: AppColors.primaryDark,
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      chipTheme: const ChipThemeData(
        backgroundColor: Colors.white,
        selectedColor: AppColors.primary,
        secondarySelectedColor: AppColors.primary,
        disabledColor: AppColors.border,
        labelStyle: TextStyle(
            color: AppColors.textPrimary, fontWeight: FontWeight.w600),
        secondaryLabelStyle:
            TextStyle(color: Colors.white, fontWeight: FontWeight.w600),
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        shape: StadiumBorder(side: BorderSide(color: AppColors.border)),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: dark ? Colors.white.withValues(alpha: .06) : Colors.white,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide:
              BorderSide(color: dark ? Colors.white12 : AppColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary, width: 1.2),
        ),
        hintStyle:
            TextStyle(color: dark ? Colors.white60 : AppColors.textMuted),
      ),
    );
  }
}
