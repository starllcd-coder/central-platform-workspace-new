import 'package:flutter/material.dart';

import '../theme/app_theme.dart';

class NeoCard extends StatelessWidget {
  const NeoCard({super.key, required this.child, this.padding = const EdgeInsets.all(16)});

  final Widget child;
  final EdgeInsets padding;

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final bg = Theme.of(context).cardColor;
    return AnimatedContainer(
      duration: const Duration(milliseconds: 220),
      padding: padding,
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: dark ? Colors.white10 : AppColors.border),
        boxShadow: dark
            ? [
                const BoxShadow(color: Color(0x400A0F18), offset: Offset(0, 14), blurRadius: 24),
              ]
            : const [
                BoxShadow(color: Color(0x120B1F3A), offset: Offset(0, 12), blurRadius: 26),
              ],
      ),
      child: child,
    );
  }
}
