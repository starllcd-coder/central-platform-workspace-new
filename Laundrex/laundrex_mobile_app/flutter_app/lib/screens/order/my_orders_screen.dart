import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../core/widgets/shimmer_box.dart';
import '../../main.dart';
import 'cart_screen.dart';
import 'order_tracking_screen.dart';

class MyOrdersScreen extends StatefulWidget {
  const MyOrdersScreen({super.key});

  @override
  State<MyOrdersScreen> createState() => _MyOrdersScreenState();
}

class _MyOrdersScreenState extends State<MyOrdersScreen> {
  bool loading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    await LaundrexScope.of(context).store.fetchOrders();
    if (!mounted) return;
    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    final orders = store.orders;
    return Scaffold(
      appBar: AppBar(title: Text(tr(context, en: 'My orders', ar: 'طلباتي'))),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView.separated(
          padding: const EdgeInsets.all(18),
          itemBuilder: (context, index) {
            if (loading) {
              return const NeoCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    ShimmerBox(height: 18, width: 140),
                    SizedBox(height: 10),
                    ShimmerBox(height: 14, width: 220),
                    SizedBox(height: 12),
                    ShimmerBox(height: 16, width: 180),
                  ],
                ),
              );
            }
            if (orders.isEmpty && index == 0) {
              return NeoCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Container(
                      width: 64,
                      height: 64,
                      decoration: BoxDecoration(
                        color: AppColors.primarySoft,
                        borderRadius: BorderRadius.circular(22),
                        border: Border.all(color: AppColors.border),
                      ),
                      child: const Icon(Icons.receipt_long_rounded, size: 34, color: AppColors.primary),
                    ),
                    const SizedBox(height: 12),
                    Text(tr(context, en: 'No orders yet', ar: 'لا توجد طلبات بعد'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
                    const SizedBox(height: 6),
                    Text(tr(context, en: 'Place your first order and track it here.', ar: 'أنشئ طلبك الأول وتتبعه من هنا.'), style: Theme.of(context).textTheme.bodyMedium),
                    const SizedBox(height: 14),
                    ElevatedButton(
                      onPressed: () => AppNavigator.push(context, const CartScreen()),
                      child: Text(tr(context, en: 'Start an order', ar: 'ابدأ طلبًا')),
                    ),
                  ],
                ),
              );
            }
            if (index == 0) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(child: _StatCard(title: tr(context, en: 'Recent', ar: 'الأحدث'), value: tr(context, en: 'Last 7 days', ar: 'آخر 7 أيام'))),
                      const SizedBox(width: 12),
                      Expanded(child: _StatCard(title: tr(context, en: 'Total', ar: 'الإجمالي'), value: '${orders.length} ${tr(context, en: 'orders', ar: 'طلبات')}')),
                    ],
                  ),
                  const SizedBox(height: 12),
                  if (store.hasLastOrder)
                    Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: OutlinedButton.icon(
                        onPressed: () {
                          store.reorderLastOrder();
                          AppNavigator.push(context, const CartScreen());
                        },
                        icon: const Icon(Icons.refresh_rounded),
                        label: Text(tr(context, en: 'Reorder last order', ar: 'إعادة طلب آخر طلب')),
                      ),
                    ),
                  _orderCard(context, orders[index]),
                ],
              );
            }
            return _orderCard(context, orders[index]);
          },
          separatorBuilder: (_, __) => const SizedBox(height: 12),
          itemCount: loading ? 3 : (orders.isEmpty ? 1 : orders.length),
        ),
      ),
    );
  }

  Widget _orderCard(BuildContext context, order) {
    final color = _statusColor(order.status.toString());
    final store = LaundrexScope.of(context).store;
    return GestureDetector(
      onTap: () async {
        await AppNavigator.push(
          context,
          OrderTrackingScreen(orderId: order.id, orderCode: order.code, status: order.status),
        );
        await store.fetchOrders();
        if (mounted) setState(() {});
      },
      child: NeoCard(
        child: Row(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: AppColors.primarySoft,
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: AppColors.border),
              ),
              child: const Icon(Icons.receipt_long_rounded, color: AppColors.primary),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(child: Text(order.code, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16))),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: .12),
                          borderRadius: BorderRadius.circular(999),
                          border: Border.all(color: color.withValues(alpha: .24)),
                        ),
                        child: Text(order.status, style: TextStyle(color: color, fontWeight: FontWeight.w800, fontSize: 12)),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(order.laundryName),
                  const SizedBox(height: 6),
                  Text('${order.amount} - ${order.placedAt}', style: Theme.of(context).textTheme.bodyMedium),
                ],
              ),
            ),
            const SizedBox(width: 8),
            const Icon(Icons.chevron_right_rounded, color: AppColors.textMuted),
          ],
        ),
      ),
    );
  }

  Color _statusColor(String status) {
    final normalized = status.toUpperCase();
    if (normalized.contains('READY') || normalized.contains('DELIVER')) return AppColors.success;
    if (normalized.contains('PENDING') || normalized.contains('WASH')) return AppColors.warning;
    return AppColors.primary;
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({required this.title, required this.value});

  final String title;
  final String value;

  @override
  Widget build(BuildContext context) {
    return NeoCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: Theme.of(context).textTheme.bodyMedium),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w800, color: AppColors.primaryDark)),
        ],
      ),
    );
  }
}
