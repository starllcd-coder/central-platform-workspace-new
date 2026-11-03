import 'package:flutter/material.dart';

class AppNavigator {
  static Future<T?> push<T>(BuildContext context, Widget page) {
    return Navigator.of(context).push<T>(_route(page));
  }

  static Future<T?> replace<T>(BuildContext context, Widget page) {
    return Navigator.of(context).pushReplacement<T, T>(_route(page));
  }

  static PageRouteBuilder<T> _route<T>(Widget page) {
    return PageRouteBuilder<T>(
      pageBuilder: (_, animation, __) => FadeTransition(
        opacity: animation,
        child: SlideTransition(
          position: Tween(begin: const Offset(.06, 0), end: Offset.zero).animate(
            CurvedAnimation(parent: animation, curve: Curves.easeOutCubic),
          ),
          child: page,
        ),
      ),
      transitionDuration: const Duration(milliseconds: 320),
    );
  }
}
