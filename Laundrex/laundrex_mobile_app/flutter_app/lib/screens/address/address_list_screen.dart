import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../core/widgets/shimmer_box.dart';
import '../../main.dart';
import '../../models/models.dart';
import 'address_form_screen.dart';

class AddressListScreen extends StatefulWidget {
  const AddressListScreen({super.key});

  @override
  State<AddressListScreen> createState() => _AddressListScreenState();
}

class _AddressListScreenState extends State<AddressListScreen> {
  bool loading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    await LaundrexScope.of(context).store.fetchAddresses();
    if (!mounted) return;
    setState(() => loading = false);
  }

  Future<void> _openAddAddress() async {
    final changed = await AppNavigator.push<bool>(context, const AddressFormScreen());
    if (!mounted) return;
    if (changed == true) {
      await _load();
    }
  }

  Future<void> _openEditAddress(AddressModel address) async {
    final changed = await AppNavigator.push<bool>(context, AddressFormScreen(initial: address));
    if (!mounted) return;
    if (changed == true) {
      await _load();
    }
  }

  Future<void> _deleteAddress(int addressId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(tr(context, en: 'Delete address', ar: 'حذف العنوان')),
        content: Text(tr(context, en: 'Do you want to delete this address?', ar: 'هل تريد حذف هذا العنوان؟')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text(tr(context, en: 'Cancel', ar: 'إلغاء'))),
          TextButton(onPressed: () => Navigator.pop(context, true), child: Text(tr(context, en: 'Delete', ar: 'حذف'))),
        ],
      ),
    );
    if (!mounted || confirmed != true) return;
    final message = await LaundrexScope.of(context).store.deleteAddressRemote(addressId);
    if (!mounted) return;
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      return;
    }
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    final addresses = LaundrexScope.of(context).store.addresses;
    return Scaffold(
      appBar: AppBar(title: Text(tr(context, en: 'Saved addresses', ar: 'العناوين المحفوظة'))),
      floatingActionButton: FloatingActionButton.extended(
        backgroundColor: AppColors.primary,
        foregroundColor: Colors.white,
        onPressed: _openAddAddress,
        icon: const Icon(Icons.add_location_alt_outlined),
        label: Text(tr(context, en: 'Add address', ar: 'إضافة عنوان')),
      ),
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
                  ],
                ),
              );
            }
            if (addresses.isEmpty && index == 0) {
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
                      child: const Icon(Icons.location_on_rounded, size: 34, color: AppColors.primary),
                    ),
                    const SizedBox(height: 12),
                    Text(tr(context, en: 'No addresses yet', ar: 'لا توجد عناوين بعد'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
                    const SizedBox(height: 6),
                    Text(tr(context, en: 'Add your pickup location to place orders faster.', ar: 'أضف موقع الاستلام لتقديم الطلبات بسرعة.'), style: Theme.of(context).textTheme.bodyMedium),
                  ],
                ),
              );
            }
            final address = addresses[index];
            return NeoCard(
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
                    child: const Icon(Icons.location_on_rounded, color: AppColors.primary),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(address.label, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                            if (address.isDefault)
                              Container(
                                margin: const EdgeInsets.only(left: 8),
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: AppColors.success.withValues(alpha: .12),
                                  borderRadius: BorderRadius.circular(20),
                                  border: Border.all(color: AppColors.success.withValues(alpha: .22)),
                                ),
                                child: Text(tr(context, en: 'Default', ar: 'افتراضي'), style: const TextStyle(color: AppColors.success, fontWeight: FontWeight.w700, fontSize: 12)),
                              ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        Text(address.line1),
                        if (address.line2.isNotEmpty) Text(address.line2),
                      ],
                    ),
                  ),
                  PopupMenuButton<String>(
                    onSelected: (value) {
                      if (value == 'edit') {
                        _openEditAddress(address);
                        return;
                      }
                      _deleteAddress(address.id);
                    },
                    itemBuilder: (context) => [
                      PopupMenuItem(value: 'edit', child: Text(tr(context, en: 'Edit', ar: 'تعديل'))),
                      PopupMenuItem(value: 'delete', child: Text(tr(context, en: 'Delete', ar: 'حذف'))),
                    ],
                  ),
                ],
              ),
            );
          },
          separatorBuilder: (_, __) => const SizedBox(height: 12),
          itemCount: loading ? 3 : (addresses.isEmpty ? 1 : addresses.length),
        ),
      ),
    );
  }
}
