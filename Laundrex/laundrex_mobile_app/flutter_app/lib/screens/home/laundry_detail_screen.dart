import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../core/widgets/shimmer_box.dart';
import '../../main.dart';
import '../../models/models.dart';
import '../order/cart_screen.dart';

class LaundryDetailScreen extends StatefulWidget {
  const LaundryDetailScreen({super.key, required this.laundry});

  final Laundry laundry;

  @override
  State<LaundryDetailScreen> createState() => _LaundryDetailScreenState();
}

class _LaundryDetailScreenState extends State<LaundryDetailScreen> {
  static const String _allKey = '__all__';
  String category = _allKey;
  String query = '';
  bool loading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    await LaundrexScope.of(context).store.fetchCatalog(widget.laundry.id);
    if (!mounted) return;
    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    return AnimatedBuilder(
      animation: store,
      builder: (context, _) {
        final isAr = isArabicLocale(context);
        final allLabel = tr(context, en: 'All', ar: '????');
        final categoryValues = <String>[_allKey, ...{...store.catalog.map((e) => 'service:${e.serviceId}')}];
        final categoryLabels = <String, String>{_allKey: allLabel};

        for (final value in categoryValues) {
          if (value == _allKey) continue;
          final id = int.tryParse(value.split(':').last);
          final sample = store.catalog.cast<CatalogItem?>().firstWhere((e) => e?.serviceId == id, orElse: () => null);
          if (sample != null) {
            categoryLabels[value] = _serviceLabel(sample, isAr);
          }
        }

        final items = category == _allKey
            ? store.catalog
            : store.catalog.where((e) => 'service:${e.serviceId}' == category).toList();
        final filteredItems = _applySearch(items, isAr);
        final selectedQty = store.cart.values.fold<int>(0, (sum, qty) => sum + qty);
        final selectedTotal = store.catalog
            .where((item) => store.cart.containsKey(item.id))
            .fold<double>(0, (sum, item) => sum + (item.price * (store.cart[item.id] ?? 0)));

        return Scaffold(
          appBar: AppBar(
            title: Text(widget.laundry.name),
            actions: [
              Padding(
                padding: const EdgeInsets.only(right: 14),
                child: InkWell(
                  borderRadius: BorderRadius.circular(16),
                  onTap: () => AppNavigator.push(context, const CartScreen()),
                  child: Container(
                    height: 44,
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.shopping_bag_outlined, color: AppColors.primaryDark, size: 20),
                        const SizedBox(width: 6),
                        Text(
                          tr(context, en: 'Add to Cart', ar: '??? ?????'),
                          style: const TextStyle(fontWeight: FontWeight.w700, color: AppColors.primaryDark),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
                  ],
                ),
          floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
          floatingActionButton: selectedQty > 0
              ? Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 18),
                  child: SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () => AppNavigator.push(context, const CartScreen()),
                      icon: const Icon(Icons.shopping_bag_outlined),
                      label: Text(
                        '${tr(context, en: 'View Cart', ar: '??? ?????')} ($selectedQty) - ${tr(context, en: 'OMR', ar: '?.?')} ${selectedTotal.toStringAsFixed(3)}',
                      ),
                    ),
                  ),
                )
              : null,
          body: loading
              ? ListView(
                  padding: const EdgeInsets.all(18),
                  children: const [
                    NeoCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          ShimmerBox(height: 22, width: 180),
                          SizedBox(height: 10),
                          ShimmerBox(height: 14, width: 240),
                          SizedBox(height: 14),
                          ShimmerBox(height: 52),
                        ],
                      ),
                    ),
                    SizedBox(height: 14),
                    NeoCard(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          ShimmerBox(height: 18, width: 140),
                          SizedBox(height: 12),
                          ShimmerBox(height: 14, width: 220),
                          SizedBox(height: 10),
                          ShimmerBox(height: 18, width: 120),
                        ],
                      ),
                    ),
                  ],
                )
              : ListView(
                  padding: const EdgeInsets.all(18),
                  children: [
                    Hero(
                      tag: 'laundry-${widget.laundry.id}',
                      child: Material(
                        color: Colors.transparent,
                        child: NeoCard(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Container(
                                    width: 72,
                                    height: 72,
                                    decoration: BoxDecoration(
                                      color: AppColors.primarySoft,
                                      borderRadius: BorderRadius.circular(24),
                                      border: Border.all(color: AppColors.border),
                                    ),
                                    child: const Icon(Icons.local_laundry_service_rounded, color: AppColors.primary, size: 34),
                                  ),
                                  const SizedBox(width: 14),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text(widget.laundry.name, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
                                        const SizedBox(height: 6),
                                        Text(widget.laundry.subtitle),
                                        const SizedBox(height: 10),
                                        Wrap(
                                          spacing: 8,
                                          runSpacing: 8,
                                          children: [
                                            _infoChip(Icons.star_rounded, '${widget.laundry.rating}'),
                                            _infoChip(Icons.timer_outlined, widget.laundry.eta),
                                            _infoChip(Icons.location_on_outlined, widget.laundry.city),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      height: 42,
                      child: Stack(
                        children: [
                          ListView.separated(
                            scrollDirection: Axis.horizontal,
                            itemBuilder: (context, index) {
                              final value = categoryValues[index];
                              final label = categoryLabels[value] ?? value;
                              final selected = value == category;
                              return ChoiceChip(
                                showCheckmark: false,
                                selectedColor: AppColors.primaryDark,
                                backgroundColor: Colors.white,
                                side: BorderSide(
                                  color: selected ? AppColors.primaryDark : AppColors.border,
                                ),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
                                avatar: selected
                                    ? const Icon(Icons.check_rounded, size: 16, color: Colors.white)
                                    : null,
                                labelStyle: TextStyle(
                                  color: selected ? Colors.white : AppColors.textPrimary,
                                  fontWeight: selected ? FontWeight.w800 : FontWeight.w600,
                                ),
                                label: Text(label),
                                selected: selected,
                                onSelected: (_) => setState(() => category = value),
                              );
                            },
                            separatorBuilder: (_, __) => const SizedBox(width: 8),
                            itemCount: categoryValues.length,
                          ),
                          IgnorePointer(
                            child: Align(
                              alignment: Alignment.centerLeft,
                              child: Container(
                                width: 24,
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    begin: Alignment.centerLeft,
                                    end: Alignment.centerRight,
                                    colors: [
                                      AppColors.background,
                                      AppColors.background.withValues(alpha: 0),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                          IgnorePointer(
                            child: Align(
                              alignment: Alignment.centerRight,
                              child: Container(
                                width: 24,
                                decoration: BoxDecoration(
                                  gradient: LinearGradient(
                                    begin: Alignment.centerRight,
                                    end: Alignment.centerLeft,
                                    colors: [
                                      AppColors.background,
                                      AppColors.background.withValues(alpha: 0),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 18),
                    TextField(
                      onChanged: (value) => setState(() => query = value),
                      decoration: InputDecoration(
                        hintText: tr(context, en: 'Search item...', ar: '???? ?? ???...'),
                        prefixIcon: const Icon(Icons.search_rounded),
                        suffixIcon: query.trim().isEmpty
                            ? null
                            : IconButton(
                                onPressed: () => setState(() => query = ''),
                                icon: const Icon(Icons.close_rounded),
                              ),
                        filled: true,
                        fillColor: Colors.white,
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: const BorderSide(color: AppColors.border),
                        ),
                        enabledBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: const BorderSide(color: AppColors.border),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(14),
                          borderSide: const BorderSide(color: AppColors.primary),
                        ),
                      ),
                    ),
                    const SizedBox(height: 14),
                    if (items.isEmpty)
                      NeoCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              tr(context, en: 'No items available yet', ar: '?? ???? ????? ????? ??????'),
                              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              store.catalogUsingFallback
                                  ? tr(
                                      context,
                                      en: 'Live catalog is unavailable right now. Showing fallback data may be limited.',
                                      ar: '?????? ??????? ??? ???? ????. ?? ???? ???????? ??????? ??????.',
                                    )
                                  : tr(
                                      context,
                                      en: 'This laundry has not published a catalog for the selected service category.',
                                      ar: '??? ??????? ?? ???? ???????? ???? ?????? ???????.',
                                    ),
                              style: Theme.of(context).textTheme.bodyMedium,
                            ),
                          ],
                        ),
                      )
                    else if (filteredItems.isEmpty)
                      NeoCard(
                        child: Text(
                          tr(context, en: 'No items match your search.', ar: '?? ???? ????? ????? ?????.'),
                          style: Theme.of(context).textTheme.bodyMedium,
                        ),
                      )
                    else
                      ...filteredItems.map(
                        (item) => Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: NeoCard(
                            child: Row(
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(_itemLabel(item, isAr), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
                                      const SizedBox(height: 8),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                        decoration: BoxDecoration(
                                          color: AppColors.primarySoft,
                                          borderRadius: BorderRadius.circular(999),
                                          border: Border.all(color: AppColors.border),
                                        ),
                                        child: Text(
                                          _serviceLabel(item, isAr),
                                          style: const TextStyle(fontWeight: FontWeight.w700, color: AppColors.primaryDark),
                                        ),
                                      ),
                                      const SizedBox(height: 8),
                                      Text(
                                        '${tr(context, en: 'OMR', ar: '?.?')} ${item.price.toStringAsFixed(3)}',
                                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: AppColors.primaryDark),
                                      ),
                                    ],
                                  ),
                                ),
                                _QtyButton(onTap: () => store.removeFromCart(item.id), icon: Icons.remove_rounded),
                                Padding(
                                  padding: const EdgeInsets.symmetric(horizontal: 12),
                                  child: Text(
                                    '${store.cart[item.id] ?? 0}',
                                    style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                                  ),
                                ),
                                _QtyButton(onTap: () => store.addToCart(item.id), icon: Icons.add_rounded),
                              ],
                            ),
                          ),
                        ),
                      ),
                    SizedBox(height: selectedQty > 0 ? 92 : 8),
                  ],
                ),
        );
      },
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

  List<CatalogItem> _applySearch(List<CatalogItem> source, bool isAr) {
    final q = query.trim().toLowerCase();
    if (q.isEmpty) return source;
    return source.where((item) {
      final enName = item.name.toLowerCase();
      final arName = item.nameAr.toLowerCase();
      final serviceEn = item.serviceName.toLowerCase();
      final serviceAr = item.serviceNameAr.toLowerCase();
      final label = _itemLabel(item, isAr).toLowerCase();
      return enName.contains(q) || arName.contains(q) || serviceEn.contains(q) || serviceAr.contains(q) || label.contains(q);
    }).toList();
  }

  Widget _infoChip(IconData icon, String label) {
    return Container(
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
          Text(label, style: const TextStyle(fontWeight: FontWeight.w700, color: AppColors.textPrimary)),
        ],
      ),
    );
  }
}

class _QtyButton extends StatelessWidget {
  const _QtyButton({required this.onTap, required this.icon});

  final VoidCallback onTap;
  final IconData icon;

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          width: 36,
          height: 36,
          alignment: Alignment.center,
          decoration: BoxDecoration(
            color: AppColors.primaryDark,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.primaryDeep, width: 1.2),
            boxShadow: [
              BoxShadow(
                color: AppColors.primaryDark.withValues(alpha: 0.28),
                blurRadius: 8,
                offset: const Offset(0, 3),
              ),
            ],
          ),
          child: Icon(icon, color: Colors.white, size: 20),
        ),
      ),
    );
  }
}

