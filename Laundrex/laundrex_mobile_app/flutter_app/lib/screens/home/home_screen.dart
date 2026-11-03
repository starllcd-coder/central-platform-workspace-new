import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../core/widgets/shimmer_box.dart';
import '../../main.dart';
import '../order/cart_screen.dart';
import '../profile/notifications_screen.dart';
import 'laundry_detail_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool loading = true;
  String query = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    final store = LaundrexScope.of(context).store;
    await store.fetchLaundries();
    await store.fetchNotifications();
    if (!mounted) return;
    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    return AnimatedBuilder(
      animation: store,
      builder: (context, _) {
        final baseLaundries = store.visibleLaundries;
        final cartItems = store.catalog.where((item) => store.cart.containsKey(item.id)).toList();
        final cartQty = cartItems.fold<int>(0, (sum, item) => sum + (store.cart[item.id] ?? 0));
        final laundries = baseLaundries.where((e) {
          final q = query.toLowerCase();
          return e.name.toLowerCase().contains(q) || e.city.toLowerCase().contains(q) || e.subtitle.toLowerCase().contains(q);
        }).toList();
        return Scaffold(
      bottomNavigationBar: cartQty > 0
          ? SafeArea(
              minimum: const EdgeInsets.fromLTRB(18, 0, 18, 14),
              child: NeoCard(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(
                            '$cartQty ${tr(context, en: 'items selected', ar: '???? ????')}',
                            style: const TextStyle(fontWeight: FontWeight.w700),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'OMR ${store.subtotal.toStringAsFixed(3)}',
                            style: const TextStyle(fontWeight: FontWeight.w800, color: AppColors.primaryDark),
                          ),
                        ],
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: () => AppNavigator.push(context, const CartScreen()),
                      icon: const Icon(Icons.shopping_bag_outlined),
                      label: Text(tr(context, en: 'Go to Cart', ar: '???? ??? ?????')),
                    ),
                  ],
                ),
              ),
            )
          : null,
      appBar: AppBar(
        automaticallyImplyLeading: false,
        title: Text(tr(context, en: 'Dashboard', ar: '????????')),
        actions: [
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: _TopActionButton(
              icon: Icons.notifications_none_rounded,
              badge: store.unreadNotifications > 0,
              onTap: () async {
                await AppNavigator.push(context, const NotificationsScreen());
                if (!mounted) return;
                await store.fetchNotifications();
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.only(right: 14),
            child: _TopActionButton(
              icon: Icons.shopping_bag_outlined,
              badge: cartQty > 0,
              onTap: () => AppNavigator.push(context, const CartScreen()),
            ),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.fromLTRB(18, 8, 18, 24),
          children: [
            Text(tr(context, en: 'Overview', ar: '???? ????'), style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            NeoCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    tr(context, en: 'Welcome back', ar: '?????? ??????'),
                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${tr(context, en: 'Customer', ar: '??????')}: ${store.userName}',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  if (store.selectedCity.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
                      decoration: BoxDecoration(
                        color: AppColors.primarySoft,
                        borderRadius: BorderRadius.circular(999),
                        border: Border.all(color: AppColors.border),
                      ),
                      child: Text(
                        '${tr(context, en: 'City', ar: '???????')}: ${store.selectedCity}',
                        style: const TextStyle(fontWeight: FontWeight.w700, color: AppColors.primaryDark),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 18),
            Row(
              children: [
                Expanded(
                  child: _SummaryCard(
                    title: tr(context, en: 'Nearby', ar: '?????? ???'),
                    value: '${baseLaundries.length}',
                    subtitle: tr(context, en: 'Shops available', ar: '????? ?????'),
                    pill: tr(context, en: 'Live', ar: '?????'),
                    pillColor: AppColors.info,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _SummaryCard(
                    title: tr(context, en: 'Cart', ar: '?????'),
                    value: '$cartQty',
                    subtitle: tr(context, en: 'Pieces selected', ar: '??? ?????'),
                    pill: 'OMR ${store.subtotal.toStringAsFixed(3)}',
                    pillColor: AppColors.primary,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            TextField(
              onChanged: (value) => setState(() => query = value),
              decoration: InputDecoration(
                prefixIcon: const Icon(Icons.search_rounded),
                hintText: tr(context, en: 'Search laundry, city, service', ar: '???? ?? ????? ?? ????? ?? ????'),
              ),
            ),
            const SizedBox(height: 16),
            const _PromoBanner(),
            const SizedBox(height: 18),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(tr(context, en: 'Nearby laundries', ar: '??????? ???????'), style: Theme.of(context).textTheme.titleLarge),
                Text('${laundries.length} ${tr(context, en: 'found', ar: '?????')}', style: Theme.of(context).textTheme.bodyMedium),
              ],
            ),
            const SizedBox(height: 12),
            if (loading)
              ...List.generate(
                3,
                (_) => const Padding(
                  padding: EdgeInsets.only(bottom: 14),
                  child: NeoCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        ShimmerBox(height: 18, width: 160),
                        SizedBox(height: 12),
                        ShimmerBox(height: 14, width: 120),
                        SizedBox(height: 16),
                        ShimmerBox(height: 52),
                      ],
                    ),
                  ),
                ),
              )
            else if (laundries.isEmpty)
              NeoCard(
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
                      child: const Icon(Icons.location_city_outlined, size: 32, color: AppColors.primary),
                    ),
                    const SizedBox(height: 12),
                    Text(tr(context, en: 'No laundries in this city yet', ar: '?? ???? ????? ?? ??? ??????? ???'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
                    const SizedBox(height: 6),
                    Text(
                      store.selectedCity.isEmpty
                          ? tr(context, en: 'Try another search term.', ar: '???? ???? ??? ????.')
                          : tr(context, en: 'Change your preferred city in profile to view other locations.', ar: '???? ?????? ??????? ?? ????? ?????? ???? ????? ????.'),
                      style: Theme.of(context).textTheme.bodyMedium,
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              )
            else
              ...laundries.map(
                (laundry) => Padding(
                  padding: const EdgeInsets.only(bottom: 14),
                  child: GestureDetector(
                    onTap: () {
                      store.setSelectedLaundry(laundry);
                      AppNavigator.push(context, LaundryDetailScreen(laundry: laundry));
                    },
                    child: Hero(
                      tag: 'laundry-${laundry.id}',
                      child: Material(
                        color: Colors.transparent,
                        child: NeoCard(
                          child: Row(
                            children: [
                              Container(
                                width: 64,
                                height: 64,
                                decoration: BoxDecoration(
                                  color: AppColors.primarySoft,
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(color: AppColors.border),
                                ),
                                child: const Icon(Icons.local_laundry_service_rounded, color: AppColors.primary, size: 32),
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(laundry.name, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800)),
                                    const SizedBox(height: 6),
                                    Text(laundry.subtitle),
                                    const SizedBox(height: 10),
                                    Wrap(
                                      spacing: 8,
                                      runSpacing: 8,
                                      children: [
                                        _chip(Icons.star_rounded, '${laundry.rating}'),
                                        _chip(Icons.location_on_outlined, laundry.city),
                                        _chip(Icons.timer_outlined, laundry.eta),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 12),
                              const Icon(Icons.chevron_right_rounded, color: AppColors.textMuted),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            SizedBox(height: cartQty > 0 ? 86 : 0),
          ],
        ),
          ),
        );
      },
    );
  }

  Widget _chip(IconData icon, String label) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 14, color: AppColors.primaryDark),
            const SizedBox(width: 5),
            Text(label, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w700)),
          ],
        ),
      );
}

class _TopActionButton extends StatelessWidget {
  const _TopActionButton({required this.icon, required this.onTap, this.badge = false});

  final IconData icon;
  final VoidCallback onTap;
  final bool badge;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: onTap,
      child: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.border),
        ),
        child: Stack(
          alignment: Alignment.center,
          children: [
            Icon(icon, color: AppColors.primaryDark),
            if (badge)
              Positioned(
                top: 9,
                right: 9,
                child: Container(
                  width: 10,
                  height: 10,
                  decoration: const BoxDecoration(color: AppColors.warning, shape: BoxShape.circle),
                ),
              ),
          ],
        ),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  const _SummaryCard({
    required this.title,
    required this.value,
    required this.subtitle,
    required this.pill,
    required this.pillColor,
  });

  final String title;
  final String value;
  final String subtitle;
  final String pill;
  final Color pillColor;

  @override
  Widget build(BuildContext context) {
    return NeoCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title, style: const TextStyle(fontWeight: FontWeight.w700)),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: pillColor.withValues(alpha: .1),
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: pillColor.withValues(alpha: .22)),
                ),
                child: Text(pill, style: TextStyle(color: pillColor, fontWeight: FontWeight.w800, fontSize: 12)),
              ),
            ],
          ),
          const SizedBox(height: 18),
          Text(value, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: AppColors.primaryDark)),
          const SizedBox(height: 6),
          Text(subtitle, style: Theme.of(context).textTheme.bodyMedium),
        ],
      ),
    );
  }
}

class _PromoBanner extends StatelessWidget {
  const _PromoBanner();

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: const LinearGradient(colors: [AppColors.primaryDeep, AppColors.primary]),
          boxShadow: const [BoxShadow(color: Color(0x24134B8A), blurRadius: 22, offset: Offset(0, 12))],
        ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'New Order', ar: '??? ????'), style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 22)),
                const SizedBox(height: 8),
                Text(tr(context, en: 'Use code FRESH20 for your first pickup discount.', ar: '?????? ????? FRESH20 ???? ??? ??? ??????.'), style: const TextStyle(color: Colors.white70)),
              ],
            ),
          ),
          const SizedBox(width: 14),
          const Icon(Icons.local_offer_outlined, color: Colors.white, size: 32),
        ],
      ),
    );
  }
}

