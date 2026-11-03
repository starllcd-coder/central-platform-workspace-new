import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class GradientScaffold extends StatelessWidget {
  const GradientScaffold({super.key, required this.child, this.safeTop = true});

  final Widget child;
  final bool safeTop;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final body = Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: dark
              ? const [Color(0xFF101A2D), Color(0xFF0E1424), Color(0xFF131E34)]
              : const [Color(0xFFF9FBFF), Color(0xFFF3F8FF), Color(0xFFEEF5FF)],
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              height: 150,
              decoration: BoxDecoration(
                color: dark ? Colors.white.withValues(alpha: .03) : Colors.white.withValues(alpha: .75),
                border: Border(
                  bottom: BorderSide(
                    color: dark ? Colors.white10 : AppColors.border,
                  ),
                ),
              ),
            ),
          ),
          Positioned(
            top: -70,
            left: -55,
            child: _bubble(dark ? const Color(0x141A55A5) : const Color(0x1C1A55A5), 220),
          ),
          Positioned(
            top: 100,
            right: -45,
            child: _bubble(dark ? const Color(0x1200B8D9) : const Color(0x1200B8D9), 160),
          ),
          Positioned(
            top: 220,
            left: 20,
            right: 20,
            child: Container(
              height: 180,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(36),
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: dark
                      ? const [Color(0x0FFFFFFF), Color(0x05FFFFFF)]
                      : const [Color(0x99FFFFFF), Color(0x55EEF5FF)],
                ),
                border: Border.all(color: dark ? Colors.white10 : AppColors.border),
              ),
            ),
          ),
          Positioned(
            bottom: -105,
            left: -30,
            child: _bubble(dark ? const Color(0x0FFFFFFF) : const Color(0x162D74DA), 180),
          ),
          safeTop ? SafeArea(child: child) : child,
        ],
      ),
    );
    return Scaffold(body: body);
  }

  Widget _bubble(Color color, double size) => Container(
        width: size,
        height: size,
        decoration: BoxDecoration(shape: BoxShape.circle, color: color),
      );
}
