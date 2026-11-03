import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';
import '../../models/models.dart';
import 'checkout_screen.dart';

class CartScreen extends StatelessWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    return AnimatedBuilder(
      animation: store,
      builder: (context, _) {
        final items = store.catalog.where((e) => store.cart.containsKey(e.id)).toList();
        final isAr = isArabicLocale(context);
        final totalQty = items.fold<int>(0, (sum, item) => sum + (store.cart[item.id] ?? 0));

        return Scaffold(
          appBar: AppBar(title: Text(tr(context, en: 'Your cart', ar: 'سلة الطلب'))),
          bottomNavigationBar: items.isEmpty
              ? null
              : SafeArea(
                  minimum: const EdgeInsets.fromLTRB(18, 0, 18, 14),
                  child: NeoCard(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _line(
                          tr(context, en: 'Subtotal', ar: 'المجموع الفرعي'),
                          '${tr(context, en: 'OMR', ar: 'ر.ع')} ${store.subtotal.toStringAsFixed(3)}',
                        ),
                        const SizedBox(height: 8),
                        _line(tr(context, en: 'Items', ar: 'العناصر'), '$totalQty'),
                        const SizedBox(height: 12),
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: () => AppNavigator.push(context, const CheckoutScreen()),
                            child: Text(tr(context, en: 'Proceed to checkout', ar: 'متابعة إلى الدفع')),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
          body: items.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(18),
                    child: NeoCard(
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 68,
                            height: 68,
                            decoration: BoxDecoration(
                              color: AppColors.primarySoft,
                              borderRadius: BorderRadius.circular(24),
                              border: Border.all(color: AppColors.border),
                            ),
                            child: const Icon(Icons.shopping_bag_outlined, size: 34, color: AppColors.primary),
                          ),
                          const SizedBox(height: 14),
                          Text(
                            tr(context, en: 'Your cart is empty', ar: 'السلة فارغة'),
                            style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            tr(context, en: 'Add items from a laundry to get started.', ar: 'أضف عناصر من المغسلة للبدء.'),
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ],
                      ),
                    ),
                  ),
                )
              : Padding(
                  padding: const EdgeInsets.all(18),
                  child: ListView.separated(
                    itemCount: items.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 12),
                    itemBuilder: (context, index) {
                      final item = items[index];
                      final qty = store.cart[item.id] ?? 0;
                      final total = item.price * qty;
                      return NeoCard(
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    _itemLabel(item, isAr),
                                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                                  ),
                                  const SizedBox(height: 6),
                                  Text(
                                    _serviceLabel(item, isAr),
                                    style: const TextStyle(color: AppColors.textMuted),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    '${tr(context, en: 'OMR', ar: 'ر.ع')} ${item.price.toStringAsFixed(3)} x $qty = ${tr(context, en: 'OMR', ar: 'ر.ع')} ${total.toStringAsFixed(3)}',
                                  ),
                                ],
                              ),
                            ),
                            _StepButton(icon: Icons.remove_rounded, onTap: () => store.removeFromCart(item.id)),
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              child: Text(
                                '$qty',
                                style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                              ),
                            ),
                            _StepButton(icon: Icons.add_rounded, onTap: () => store.addToCart(item.id)),
                          ],
                        ),
                      );
                    },
                  ),
                ),
        );
      },
    );
  }

  Widget _line(String a, String b) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(a),
        Text(b, style: const TextStyle(fontWeight: FontWeight.w800)),
      ],
    );
  }

  String _itemLabel(CatalogItem item, bool isAr) {
    if (isAr && item.nameAr.trim().isNotEmpty) return item.nameAr.trim();
    return item.name;
  }

  String _serviceLabel(CatalogItem item, bool isAr) {
    if (isAr && item.serviceNameAr.trim().isNotEmpty) return item.serviceNameAr.trim();
    return item.serviceName;
  }
}

class _StepButton extends StatelessWidget {
  const _StepButton({required this.icon, required this.onTap});

  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          width: 34,
          height: 34,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: AppColors.primaryDark,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.primaryDeep),
          ),
          child: Icon(icon, size: 18, color: Colors.white),
        ),
      ),
    );
  }
}
