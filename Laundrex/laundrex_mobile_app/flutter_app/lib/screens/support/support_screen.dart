import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';

class SupportScreen extends StatelessWidget {
  const SupportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(tr(context, en: 'Support', ar: 'الدعم'))),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Need help?', ar: 'هل تحتاج مساعدة؟'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 20)),
                const SizedBox(height: 10),
                const _SupportRow(icon: Icons.mail_outline_rounded, label: 'support@laundrex.app'),
                const SizedBox(height: 8),
                const _SupportRow(icon: Icons.call_outlined, label: '+968 9000 0000'),
                const SizedBox(height: 10),
                Text(tr(context, en: 'Live chat and ticketing can be connected in the next phase.', ar: 'يمكن ربط الدردشة المباشرة والتذاكر في المرحلة القادمة.')),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SupportRow extends StatelessWidget {
  const _SupportRow({required this.icon, required this.label});

  final IconData icon;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 36,
          height: 36,
          decoration: BoxDecoration(
            color: AppColors.primarySoft,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.border),
          ),
          child: Icon(icon, size: 18, color: AppColors.primaryDark),
        ),
        const SizedBox(width: 10),
        Expanded(child: Text(label)),
      ],
    );
  }
}
