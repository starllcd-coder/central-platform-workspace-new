import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../main.dart';
import '../address/address_list_screen.dart';
import '../auth/login_screen.dart';
import '../order/my_orders_screen.dart';
import '../profile/profile_screen.dart';
import 'home_screen.dart';

class AppShell extends StatefulWidget {
  const AppShell({super.key});

  @override
  State<AppShell> createState() => _AppShellState();
}

class _AppShellState extends State<AppShell> {
  int index = 0;
  bool _redirectingToLogin = false;
  bool _shownExpiredMessage = false;
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _pollTimer = Timer.periodic(const Duration(seconds: 45), (_) async {
      if (!mounted) return;
      final store = LaundrexScope.of(context).store;
      if (!store.isLoggedIn) return;
      await store.fetchNotifications();
      await store.fetchOrders();
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    return AnimatedBuilder(
      animation: store,
      builder: (context, _) {
        if (!store.isLoggedIn) {
          if (store.sessionExpired && !_shownExpiredMessage) {
            _shownExpiredMessage = true;
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(
                    tr(
                      context,
                      en: 'Session expired. Please login again.',
                      ar: '\u0627\u0646\u062a\u0647\u062a \u0627\u0644\u062c\u0644\u0633\u0629. \u064a\u0631\u062c\u0649 \u062a\u0633\u062c\u064a\u0644 \u0627\u0644\u062f\u062e\u0648\u0644 \u0645\u0631\u0629 \u0623\u062e\u0631\u0649.',
                    ),
                  ),
                ),
              );
            });
          }
          if (!_redirectingToLogin) {
            _redirectingToLogin = true;
            WidgetsBinding.instance.addPostFrameCallback((_) {
              if (!mounted) return;
              AppNavigator.replace(context, const LoginScreen());
            });
          }
          return const SizedBox.shrink();
        }

        _redirectingToLogin = false;
        _shownExpiredMessage = false;

        const pages = [HomeScreen(), MyOrdersScreen(), AddressListScreen(), ProfileScreen()];
        return Scaffold(
          body: IndexedStack(index: index, children: pages),
          bottomNavigationBar: Container(
            margin: const EdgeInsets.fromLTRB(14, 0, 14, 14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.border),
              boxShadow: const [BoxShadow(color: Color(0x120B1F3A), blurRadius: 18, offset: Offset(0, 8))],
            ),
            child: NavigationBar(
              height: 72,
              backgroundColor: Colors.transparent,
              selectedIndex: index,
              onDestinationSelected: (value) => setState(() => index = value),
              destinations: [
                NavigationDestination(
                  icon: const Icon(Icons.home_outlined),
                  selectedIcon: const Icon(Icons.home_rounded),
                  label: tr(context, en: 'Home', ar: '\u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.receipt_long_outlined),
                  selectedIcon: const Icon(Icons.receipt_long_rounded),
                  label: tr(context, en: 'Orders', ar: '\u0627\u0644\u0637\u0644\u0628\u0627\u062a'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.location_on_outlined),
                  selectedIcon: const Icon(Icons.location_on_rounded),
                  label: tr(context, en: 'Addresses', ar: '\u0627\u0644\u0639\u0646\u0627\u0648\u064a\u0646'),
                ),
                NavigationDestination(
                  icon: const Icon(Icons.person_outline_rounded),
                  selectedIcon: const Icon(Icons.person_rounded),
                  label: tr(context, en: 'Profile', ar: '\u0627\u0644\u0645\u0644\u0641 \u0627\u0644\u0634\u062e\u0635\u064a'),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
