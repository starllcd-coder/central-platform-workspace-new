import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/app_text_field.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';
import '../../models/models.dart';
import 'map_picker_screen.dart';

class AddressFormScreen extends StatefulWidget {
  const AddressFormScreen({super.key, this.initial});

  final AddressModel? initial;

  @override
  State<AddressFormScreen> createState() => _AddressFormScreenState();
}

class _AddressFormScreenState extends State<AddressFormScreen> {
  final label = TextEditingController();
  final city = TextEditingController(text: 'Salalah');
  final area = TextEditingController();
  final details = TextEditingController();
  double? latitude;
  double? longitude;
  bool isDefault = false;
  bool loading = false;

  @override
  void initState() {
    super.initState();
    final initial = widget.initial;
    if (initial != null) {
      label.text = initial.label;
      city.text = initial.city.isEmpty ? city.text : initial.city;
      area.text = initial.area;
      details.text = initial.addressLine1.isNotEmpty ? initial.addressLine1 : initial.line1;
      latitude = initial.latitude;
      longitude = initial.longitude;
      isDefault = initial.isDefault;
    }
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final store = LaundrexScope.of(context).store;
      final preferred = store.selectedCity.trim();
      if (preferred.isNotEmpty && city.text.trim().isEmpty) {
        setState(() => city.text = preferred);
      }
    });
  }

  @override
  void dispose() {
    label.dispose();
    city.dispose();
    area.dispose();
    details.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => loading = true);
    final store = LaundrexScope.of(context).store;
    final initial = widget.initial;
    final message = initial == null
        ? await store.addAddressRemote(
            label: label.text.isEmpty ? 'Home' : label.text,
            area: area.text,
            city: city.text,
            details: details.text,
            isDefault: isDefault,
            latitude: latitude,
            longitude: longitude,
          )
        : await store.updateAddressRemote(
            addressId: initial.id,
            label: label.text.isEmpty ? 'Home' : label.text,
            area: area.text,
            city: city.text,
            details: details.text,
            isDefault: isDefault,
            latitude: latitude,
            longitude: longitude,
          );
    if (!mounted) return;
    setState(() => loading = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      if (!message.toLowerCase().contains('locally') && !message.toLowerCase().contains('updated')) {
        return;
      }
    }
    Navigator.pop(context, true);
  }

  @override
  Widget build(BuildContext context) {
    final editMode = widget.initial != null;
    return Scaffold(
      appBar: AppBar(title: Text(editMode ? tr(context, en: 'Edit address', ar: 'تعديل العنوان') : tr(context, en: 'Add address', ar: 'إضافة عنوان'))),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          NeoCard(
            child: Column(
              children: [
                AppTextField(hint: tr(context, en: 'Label (Home / Office)', ar: 'التسمية (المنزل / العمل)'), controller: label, prefixIcon: Icons.badge_outlined),
                const SizedBox(height: 12),
                AppTextField(hint: tr(context, en: 'City', ar: 'المدينة'), controller: city, prefixIcon: Icons.location_city_outlined),
                const SizedBox(height: 12),
                AppTextField(hint: tr(context, en: 'Area', ar: 'المنطقة'), controller: area, prefixIcon: Icons.map_outlined),
                const SizedBox(height: 12),
                AppTextField(hint: tr(context, en: 'Street / Building details', ar: 'تفاصيل الشارع / المبنى'), controller: details, prefixIcon: Icons.home_outlined),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () async {
                          final picked = await Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => MapPickerScreen(
                                initial: latitude != null && longitude != null ? LatLng(latitude!, longitude!) : null,
                              ),
                            ),
                          );
                          if (picked != null && picked is LatLng) {
                            setState(() {
                              latitude = picked.latitude;
                              longitude = picked.longitude;
                            });
                          }
                        },
                        icon: const Icon(Icons.map_outlined),
                        label: Text(latitude == null ? tr(context, en: 'Pick on map', ar: 'تحديد على الخريطة') : tr(context, en: 'Location selected', ar: 'تم تحديد الموقع')),
                      ),
                    ),
                  ],
                ),
                if (latitude != null && longitude != null) ...[
                  const SizedBox(height: 10),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    decoration: BoxDecoration(
                      color: AppColors.primarySoft,
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(color: AppColors.border),
                    ),
                    child: Text('${latitude!.toStringAsFixed(4)}, ${longitude!.toStringAsFixed(4)}'),
                  ),
                ],
                const SizedBox(height: 8),
                SwitchListTile(
                  contentPadding: EdgeInsets.zero,
                  value: isDefault,
                  title: Text(tr(context, en: 'Set as default', ar: 'تعيين كافتراضي')),
                  onChanged: (v) => setState(() => isDefault = v),
                ),
                const SizedBox(height: 8),
                ElevatedButton(
                  onPressed: loading ? null : _save,
                  child: loading
                      ? const SizedBox(height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : Text(editMode ? tr(context, en: 'Update address', ar: 'تحديث العنوان') : tr(context, en: 'Save address', ar: 'حفظ العنوان')),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
