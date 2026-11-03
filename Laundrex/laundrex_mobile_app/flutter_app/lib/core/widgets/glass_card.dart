import 'dart:ui';
import 'package:flutter/material.dart';

class GlassCard extends StatelessWidget {
  const GlassCard({super.key, required this.child, this.padding = const EdgeInsets.all(18)});

  final Widget child;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    final bool dark = Theme.of(context).brightness == Brightness.dark;
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10, sigmaY: 10),
        child: Container(
          padding: padding,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            color: dark ? Colors.white.withValues(alpha: .08) : Colors.white.withValues(alpha: .9),
            border: Border.all(color: dark ? Colors.white10 : const Color(0xFFE9F1FF)),
            boxShadow: [
              BoxShadow(
                blurRadius: 30,
                offset: const Offset(0, 18),
                color: Colors.black.withValues(alpha: dark ? .25 : .08),
              ),
            ],
          ),
          child: child,
        ),
      ),
    );
  }
}
