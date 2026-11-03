import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';
import '../address/address_form_screen.dart';
import 'order_success_screen.dart';

class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  bool urgent = false;
  String payment = 'COD';
  String fulfillmentMode = 'DELIVERY';
  String timeSlot = '10:00 AM - 12:00 PM';
  int? addressId;
  bool loading = false;
  Map<String, dynamic>? preview;

  final notes = TextEditingController();
  final promo = TextEditingController();
  final bankReference = TextEditingController();
  final receiptName = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  @override
  void dispose() {
    notes.dispose();
    promo.dispose();
    bankReference.dispose();
    receiptName.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final store = LaundrexScope.of(context).store;
    await store.fetchAddresses();
    if (!mounted) return;

    final addresses = store.addresses;
    setState(() {
      payment = store.preferredPayment.isEmpty ? 'COD' : store.preferredPayment;
      fulfillmentMode = store.preferredFulfillment.isEmpty ? 'DELIVERY' : store.preferredFulfillment;
      timeSlot = store.preferredTimeSlot.isEmpty ? '10:00 AM - 12:00 PM' : store.preferredTimeSlot;
      addressId = store.preferredAddressId ??
          (addresses.where((e) => e.isDefault).isNotEmpty
              ? addresses.firstWhere((e) => e.isDefault).id
              : (addresses.isEmpty ? null : addresses.first.id));
    });

    await _refreshPreview();
  }

  Future<void> _refreshPreview() async {
    final store = LaundrexScope.of(context).store;
    final promoDiscount = store.promoDiscountAmount(store.subtotal);
    final pointsUsed = store.usePoints ? store.loyaltyPoints : 0;
    final data = await store.pricePreview(
      urgent: urgent,
      promoDiscount: promoDiscount,
      pointsUsed: pointsUsed,
    );
    if (!mounted) return;
    setState(() => preview = data);
  }

  Future<void> _placeOrder() async {
    if (payment == 'BANK' && bankReference.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(tr(context, en: 'Please enter transfer reference.', ar: 'يرجى إدخال مرجع التحويل.'))),
      );
      return;
    }
    setState(() => loading = true);
    final store = LaundrexScope.of(context).store;
    final message = await store.placeOrderRemote(
      urgent: urgent,
      paymentMethod: payment,
      addressId: addressId,
      fulfillmentMode: fulfillmentMode,
      timeSlot: timeSlot,
      notes: notes.text.trim(),
      bankReference: bankReference.text.trim(),
      receiptName: receiptName.text.trim(),
    );
    if (!mounted) return;
    setState(() => loading = false);

    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      final lower = message.toLowerCase();
      final isNonBlocking = lower.contains('demo mode') || lower.contains('saved locally');
      if (!isNonBlocking) return;
    }

    AppNavigator.replace(context, const OrderSuccessScreen());
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    const allowedModes = {'DELIVERY', 'PICKUP'};
    if (!allowedModes.contains(fulfillmentMode)) {
      fulfillmentMode = 'DELIVERY';
    }

    final slots = store.availableTimeSlots.isEmpty ? const ['10:00 AM - 12:00 PM'] : store.availableTimeSlots;
    if (!slots.contains(timeSlot)) {
      timeSlot = slots.first;
    }

    final paymentMethods = store.paymentMethods.isEmpty
        ? [
            {'code': 'COD', 'label': tr(context, en: 'Cash on delivery', ar: 'الدفع عند الاستلام')},
          ]
        : store.paymentMethods.map((m) => {'code': m.code, 'label': m.label}).toList();

    final paymentCodes = paymentMethods.map((m) => (m['code'] ?? '').toString()).toSet();
    if (!paymentCodes.contains(payment)) {
      payment = paymentCodes.contains('COD') ? 'COD' : paymentCodes.first;
    }

    final urgentFee = preview?['urgent_fee'] == null
        ? (urgent ? 1.5 : 0.0)
        : double.tryParse(preview?['urgent_fee'].toString() ?? '') ?? (urgent ? 1.5 : 0.0);
    final promoDiscount = preview?['promo_discount'] == null
        ? store.promoDiscountAmount(store.subtotal)
        : double.tryParse(preview?['promo_discount'].toString() ?? '') ?? 0;
    final pointsDiscount = preview?['points_value'] == null
        ? store.redeemablePointsValue(store.subtotal + urgentFee - promoDiscount)
        : double.tryParse(preview?['points_value'].toString() ?? '') ?? 0.0;
    final subtotalValue = preview?['subtotal'] == null
        ? store.subtotal
        : double.tryParse(preview?['subtotal'].toString() ?? '') ?? store.subtotal;
    final taxValue = preview?['tax'] == null ? 0.0 : double.tryParse(preview?['tax'].toString() ?? '') ?? 0.0;
    final total = preview?['total'] == null
        ? (store.subtotal + urgentFee - promoDiscount - pointsDiscount).clamp(0, double.infinity)
        : double.tryParse(preview?['total'].toString() ?? '') ?? (store.subtotal + urgentFee - promoDiscount - pointsDiscount).clamp(0, double.infinity);
    final totalQty = store.cart.values.fold<int>(0, (sum, qty) => sum + qty);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.of(context).maybePop(),
        ),
        title: Text(tr(context, en: 'Checkout', ar: 'إتمام الطلب')),
      ),
      bottomNavigationBar: SafeArea(
        minimum: const EdgeInsets.fromLTRB(18, 0, 18, 14),
        child: NeoCard(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _line(
                tr(context, en: 'Total', ar: 'الإجمالي'),
                '${tr(context, en: 'OMR', ar: 'ر.ع')} ${total.toStringAsFixed(3)}',
                bold: true,
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: loading || store.cart.isEmpty ? null : _placeOrder,
                  child: loading
                      ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : Text(tr(context, en: 'Place order', ar: 'تأكيد الطلب')),
                ),
              ),
            ],
          ),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          _CheckoutProgress(
            steps: [
              tr(context, en: 'Mode', ar: 'الخدمة'),
              tr(context, en: 'Address', ar: 'العنوان'),
              tr(context, en: 'Payment', ar: 'الدفع'),
              tr(context, en: 'Review', ar: 'المراجعة'),
            ],
            currentStep: 3,
          ),
          const SizedBox(height: 14),
          NeoCard(
            child: Row(
              children: [
                Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(
                    color: AppColors.primarySoft,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: const Icon(Icons.shopping_bag_outlined, color: AppColors.primaryDark),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(tr(context, en: 'Review your order', ar: 'راجع طلبك'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                      const SizedBox(height: 4),
                      Text('${store.selectedLaundryName} - $totalQty ${tr(context, en: 'items', ar: 'عنصر')}'),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Service mode', ar: 'طريقة الخدمة'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                const SizedBox(height: 8),
                SegmentedButton<String>(
                  segments: [
                    ButtonSegment<String>(
                      value: 'DELIVERY',
                      label: Text(tr(context, en: 'Home delivery', ar: 'توصيل للمنزل')),
                      icon: const Icon(Icons.local_shipping_outlined),
                    ),
                    ButtonSegment<String>(
                      value: 'PICKUP',
                      label: Text(tr(context, en: 'Self pickup', ar: 'استلام ذاتي')),
                      icon: const Icon(Icons.storefront_outlined),
                    ),
                  ],
                  selected: {fulfillmentMode},
                  onSelectionChanged: (selection) async {
                    final value = selection.first;
                    setState(() => fulfillmentMode = value);
                    await store.setPreferredFulfillment(value);
                  },
                ),
                const SizedBox(height: 10),
                DropdownButtonFormField<String>(
                  initialValue: timeSlot,
                  decoration: InputDecoration(
                    hintText: tr(context, en: 'Pickup / delivery slot', ar: 'موعد الاستلام / التوصيل'),
                    prefixIcon: const Icon(Icons.schedule_outlined),
                  ),
                  items: slots.map((slot) => DropdownMenuItem<String>(value: slot, child: Text(slot))).toList(),
                  onChanged: (value) async {
                    if (value == null) return;
                    setState(() => timeSlot = value);
                    await store.setPreferredTimeSlot(value);
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(tr(context, en: 'Address', ar: 'العنوان'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                    TextButton(
                      onPressed: () => AppNavigator.push(context, const AddressFormScreen()),
                      child: Text(tr(context, en: 'Add', ar: 'إضافة')),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                if (store.addresses.isEmpty)
                  Text(tr(context, en: 'Add an address to continue.', ar: 'أضف عنواناً للمتابعة.'))
                else
                  ...store.addresses.map(
                    (address) => ListTile(
                      contentPadding: EdgeInsets.zero,
                      title: Text(address.label),
                      subtitle: Text('${address.line1}\n${address.line2}'),
                      leading: Icon(
                        addressId == address.id ? Icons.radio_button_checked : Icons.radio_button_unchecked,
                        color: addressId == address.id ? AppColors.primary : AppColors.textMuted,
                      ),
                      onTap: () {
                        setState(() => addressId = address.id);
                        store.setPreferredAddress(address.id);
                      },
                    ),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          NeoCard(
            child: SwitchListTile(
              contentPadding: EdgeInsets.zero,
              value: urgent,
              title: Text(tr(context, en: 'Urgent service', ar: 'خدمة مستعجلة')),
              subtitle: Text(tr(context, en: 'Priority cleaning with faster turnaround', ar: 'تنظيف سريع بأولوية أعلى')),
              onChanged: (v) async {
                setState(() => urgent = v);
                await _refreshPreview();
              },
            ),
          ),
          const SizedBox(height: 14),
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Promo code', ar: 'كود الخصم'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: promo,
                        decoration: InputDecoration(hintText: tr(context, en: 'Enter promo code', ar: 'أدخل كود الخصم')),
                      ),
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton(
                      onPressed: () async {
                        final message = await store.applyPromo(promo.text);
                        if (!context.mounted) return;
                        if (message != null) {
                          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
                        }
                        await _refreshPreview();
                      },
                      child: Text(tr(context, en: 'Apply', ar: 'تطبيق')),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Payment method', ar: 'طريقة الدفع'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                const SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  initialValue: payment,
                  decoration: InputDecoration(
                    hintText: tr(context, en: 'Select payment method', ar: 'اختر طريقة الدفع'),
                    prefixIcon: const Icon(Icons.payments_outlined),
                  ),
                  items: paymentMethods
                      .map((m) => DropdownMenuItem<String>(value: (m['code'] ?? '').toString(), child: Text((m['label'] ?? '').toString())))
                      .toList(),
                  onChanged: (v) {
                    if (v == null) return;
                    setState(() => payment = v);
                    store.setPreferredPayment(v);
                  },
                ),
              ],
            ),
          ),
          if (payment == 'BANK') ...[
            const SizedBox(height: 14),
            NeoCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(tr(context, en: 'Bank transfer details', ar: 'تفاصيل التحويل البنكي'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                  const SizedBox(height: 8),
                  if (store.bankTransferBankName.isNotEmpty) _line(tr(context, en: 'Bank', ar: 'البنك'), store.bankTransferBankName),
                  if (store.bankTransferAccountName.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    _line(tr(context, en: 'Account name', ar: 'اسم الحساب'), store.bankTransferAccountName),
                  ],
                  if (store.bankTransferAccountNumber.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    _line(tr(context, en: 'Account number', ar: 'رقم الحساب'), store.bankTransferAccountNumber),
                  ],
                  if (store.bankTransferIban.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    _line(tr(context, en: 'IBAN', ar: 'آيبان'), store.bankTransferIban),
                  ],
                  if (store.bankTransferInstructions.isNotEmpty) ...[
                    const SizedBox(height: 10),
                    Text(store.bankTransferInstructions, style: const TextStyle(color: AppColors.textMuted, fontWeight: FontWeight.w600)),
                  ],
                ],
              ),
            ),
            const SizedBox(height: 14),
            NeoCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(tr(context, en: 'Transfer proof', ar: 'إثبات التحويل'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                  const SizedBox(height: 8),
                  TextField(
                    controller: bankReference,
                    decoration: InputDecoration(
                      hintText: tr(context, en: 'Transaction / bank reference number', ar: 'رقم مرجع العملية / البنك'),
                      prefixIcon: const Icon(Icons.confirmation_number_outlined),
                    ),
                  ),
                  const SizedBox(height: 10),
                  TextField(
                    controller: receiptName,
                    decoration: InputDecoration(
                      hintText: tr(context, en: 'Receipt file name (optional)', ar: 'اسم ملف الإيصال (اختياري)'),
                      prefixIcon: const Icon(Icons.receipt_long_outlined),
                    ),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 14),
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Notes', ar: 'ملاحظات'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                const SizedBox(height: 8),
                TextField(
                  controller: notes,
                  maxLines: 3,
                  decoration: InputDecoration(hintText: tr(context, en: 'Gate code, building info, preferred time...', ar: 'رمز البوابة، تفاصيل المبنى، الوقت المفضل...')),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          NeoCard(
            child: Column(
              children: [
                _line(tr(context, en: 'Subtotal', ar: 'المجموع الفرعي'), '${tr(context, en: 'OMR', ar: 'ر.ع')} ${subtotalValue.toStringAsFixed(3)}'),
                const SizedBox(height: 8),
                _line(tr(context, en: 'Urgent fee', ar: 'رسوم الاستعجال'), '${tr(context, en: 'OMR', ar: 'ر.ع')} ${urgentFee.toStringAsFixed(3)}'),
                const SizedBox(height: 8),
                _line(
                  tr(context, en: 'Promo discount', ar: 'خصم الكوبون'),
                  promoDiscount > 0 ? '- ${tr(context, en: 'OMR', ar: 'ر.ع')} ${promoDiscount.toStringAsFixed(3)}' : '${tr(context, en: 'OMR', ar: 'ر.ع')} 0.000',
                ),
                const SizedBox(height: 8),
                _line(
                  tr(context, en: 'Points', ar: 'النقاط'),
                  pointsDiscount > 0 ? '- ${tr(context, en: 'OMR', ar: 'ر.ع')} ${pointsDiscount.toStringAsFixed(3)}' : '${tr(context, en: 'OMR', ar: 'ر.ع')} 0.000',
                ),
                if (taxValue > 0) ...[
                  const SizedBox(height: 8),
                  _line(tr(context, en: 'Tax', ar: 'الضريبة'), '${tr(context, en: 'OMR', ar: 'ر.ع')} ${taxValue.toStringAsFixed(3)}'),
                ],
              ],
            ),
          ),
          const SizedBox(height: 120),
        ],
      ),
    );
  }

  Widget _line(String left, String right, {bool bold = false}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(left),
        Text(
          right,
          style: TextStyle(fontWeight: bold ? FontWeight.w800 : FontWeight.w600, fontSize: bold ? 18 : 15),
        ),
      ],
    );
  }
}

class _CheckoutProgress extends StatelessWidget {
  const _CheckoutProgress({required this.steps, required this.currentStep});

  final List<String> steps;
  final int currentStep;

  @override
  Widget build(BuildContext context) {
    return NeoCard(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: [
            for (var i = 0; i < steps.length; i++) ...[
              _StepPill(
                label: steps[i],
                active: i <= currentStep,
                current: i == currentStep,
              ),
              if (i < steps.length - 1)
                Container(
                  width: 20,
                  height: 2,
                  margin: const EdgeInsets.symmetric(horizontal: 6),
                  color: i < currentStep ? AppColors.primaryDark : AppColors.border,
                ),
            ],
          ],
        ),
      ),
    );
  }
}

class _StepPill extends StatelessWidget {
  const _StepPill({
    required this.label,
    required this.active,
    required this.current,
  });

  final String label;
  final bool active;
  final bool current;

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 180),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
      decoration: BoxDecoration(
        color: active ? AppColors.primaryDark : Colors.white,
        borderRadius: BorderRadius.circular(999),
        border: Border.all(
          color: active ? AppColors.primaryDark : AppColors.border,
          width: current ? 1.6 : 1,
        ),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          fontWeight: current ? FontWeight.w800 : FontWeight.w700,
          color: active ? Colors.white : AppColors.textMuted,
        ),
      ),
    );
  }
}
