import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';

class WalletScreen extends StatelessWidget {
  const WalletScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    return Scaffold(
      appBar: AppBar(title: Text(tr(context, en: 'Wallet & offers', ar: 'المحفظة والعروض'))),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Loyalty points', ar: 'نقاط الولاء'), style: const TextStyle(fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                Text('${store.loyaltyPoints} ${tr(context, en: 'pts', ar: 'نقطة')}', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: AppColors.primaryDark)),
                const SizedBox(height: 6),
                Text('${tr(context, en: 'Value', ar: 'القيمة')}: ${tr(context, en: 'OMR', ar: 'ر.ع')} ${store.pointsValue.toStringAsFixed(3)}', style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
          ),
          const SizedBox(height: 14),
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Promo codes', ar: 'أكواد الخصم'), style: const TextStyle(fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                Text(
                  store.promoCode.isEmpty
                      ? tr(context, en: 'No promo applied.', ar: 'لا يوجد كود خصم مطبق.')
                      : '${tr(context, en: 'Applied', ar: 'تم التطبيق')}: ${store.promoCode}',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 6),
                Text('${tr(context, en: 'Try', ar: 'جرّب')}: FRESH20, FIRST10, SAVE5'),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
