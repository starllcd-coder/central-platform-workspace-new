import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';

import 'core/theme/app_theme.dart';
import 'data/mock_store.dart';
import 'screens/home/splash_screen.dart';
import 'services/notification_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const LaundrexApp());
}

class LaundrexApp extends StatefulWidget {
  const LaundrexApp({super.key});

  @override
  State<LaundrexApp> createState() => _LaundrexAppState();
}

class _LaundrexAppState extends State<LaundrexApp> {
  final MockStore store = MockStore();
  ThemeMode _themeMode = ThemeMode.light;
  Locale _locale = const Locale('en');
  final GlobalKey<ScaffoldMessengerState> _messengerKey = GlobalKey<ScaffoldMessengerState>();

  void _setThemeMode(ThemeMode mode) {
    setState(() => _themeMode = mode);
  }

  void _setLocale(Locale locale) {
    setState(() => _locale = locale);
  }

  @override
  void initState() {
    super.initState();
    _initNotifications();
  }

  Future<void> _initNotifications() async {
    final token = await NotificationService.init();
    if (!mounted) return;
    if (token != null) {
      await store.saveDeviceToken(token);
    }
    NotificationService.listenForegroundMessages((message) {
      final title = message.notification?.title ?? 'Update';
      final body = message.notification?.body ?? 'Your order status updated.';
      _messengerKey.currentState?.showSnackBar(SnackBar(content: Text('$title • $body')));
    });
  }

  @override
  Widget build(BuildContext context) {
    return LaundrexScope(
      store: store,
      setThemeMode: _setThemeMode,
      setLocale: _setLocale,
      themeMode: _themeMode,
      locale: _locale,
      child: MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Laundrex',
        scaffoldMessengerKey: _messengerKey,
        theme: AppTheme.lightTheme,
        darkTheme: AppTheme.darkTheme,
        themeMode: _themeMode,
        locale: _locale,
        supportedLocales: const [
          Locale('en'),
          Locale('ar'),
        ],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        builder: (context, child) {
          final locale = Localizations.localeOf(context);
          final isArabic = locale.languageCode.toLowerCase().startsWith('ar');
          final textTheme = AppTheme.textThemeForLocale(locale.languageCode);
          final themed = Theme.of(context).copyWith(
            textTheme: textTheme,
            primaryTextTheme: textTheme,
          );
          return Theme(
            data: themed,
            child: Directionality(
              textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
              child: child ?? const SizedBox.shrink(),
            ),
          );
        },
        home: const SplashScreen(),
      ),
    );
  }
}

class LaundrexScope extends InheritedWidget {
  const LaundrexScope({
    super.key,
    required this.store,
    required this.setThemeMode,
    required this.setLocale,
    required this.themeMode,
    required this.locale,
    required super.child,
  });

  final MockStore store;
  final ValueChanged<ThemeMode> setThemeMode;
  final ValueChanged<Locale> setLocale;
  final ThemeMode themeMode;
  final Locale locale;

  static LaundrexScope of(BuildContext context) {
    final LaundrexScope? result = context.dependOnInheritedWidgetOfExactType<LaundrexScope>();
    assert(result != null, 'No LaundrexScope found in context');
    return result!;
  }

  @override
  bool updateShouldNotify(LaundrexScope oldWidget) {
    return store != oldWidget.store || themeMode != oldWidget.themeMode || locale != oldWidget.locale;
  }
}
