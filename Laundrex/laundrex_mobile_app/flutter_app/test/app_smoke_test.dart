import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:laundrex_mobile_app/core/theme/app_theme.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  GoogleFonts.config.allowRuntimeFetching = false;

  test('theme configurations are available', () {
    final ThemeData light = AppTheme.lightTheme;
    final ThemeData dark = AppTheme.darkTheme;
    expect(light, isNotNull);
    expect(dark, isNotNull);
  });
}
