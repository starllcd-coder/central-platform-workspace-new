import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/brand_logo.dart';
import '../../core/widgets/gradient_scaffold.dart';
import '../../main.dart';
import '../auth/login_screen.dart';
import 'app_shell.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late final AnimationController _controller = AnimationController(vsync: this, duration: const Duration(milliseconds: 1200))..forward();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _bootstrap());
  }

  Future<void> _bootstrap() async {
    final store = LaundrexScope.of(context).store;
    try {
      await store.init().timeout(const Duration(seconds: 8));
      if (store.isLoggedIn) {
        await store.fetchLaundries();
        await store.fetchAddresses();
        await store.fetchOrders();
      }
    } catch (_) {
      // Allow app to continue even if init/network stalls.
    }
    if (!mounted) return;
    Timer(const Duration(seconds: 2), () {
      if (!mounted) return;
      AppNavigator.replace(context, store.isLoggedIn ? const AppShell() : const LoginScreen());
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GradientScaffold(
      child: Center(
        child: ScaleTransition(
          scale: CurvedAnimation(parent: _controller, curve: Curves.elasticOut),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              BrandLogo(
                size: MediaQuery.sizeOf(context).width < 400 ? 170 : 188,
                cropFactor: 0.82,
                useSvg: false,
              ),
              const SizedBox(height: 18),
              Text('Laundrex', style: Theme.of(context).textTheme.headlineMedium),
              const SizedBox(height: 8),
              Text(tr(context, en: 'Fresh care at your fingertips', ar: 'عناية منعشة بين يديك'), style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Colors.black54)),
            ],
          ),
        ),
      ),
    );
  }
}
