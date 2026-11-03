import 'package:flutter/material.dart';

import '../../core/utils/city_names.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/app_text_field.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';

class ProfileEditScreen extends StatefulWidget {
  const ProfileEditScreen({super.key});

  @override
  State<ProfileEditScreen> createState() => _ProfileEditScreenState();
}

class _ProfileEditScreenState extends State<ProfileEditScreen> {
  final TextEditingController _name = TextEditingController();
  final TextEditingController _phone = TextEditingController();
  final TextEditingController _email = TextEditingController();
  String _city = 'Salalah';
  bool _initialized = false;
  bool _loading = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_initialized) return;
    _initialized = true;
    final store = LaundrexScope.of(context).store;
    _name.text = store.userName;
    _phone.text = store.phone;
    _email.text = store.email;
    final cities = store.availableCities.isEmpty ? const ['Salalah', 'Muscat', 'Seeb'] : store.availableCities;
    _city = store.selectedCity.isEmpty ? cities.first : store.selectedCity;
    if (!cities.contains(_city)) {
      _city = cities.first;
    }
  }

  @override
  void dispose() {
    _name.dispose();
    _phone.dispose();
    _email.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    setState(() => _loading = true);
    final scope = LaundrexScope.of(context);
    final store = scope.store;
    final message = await store.updateProfileRemote(
      fullName: _name.text.trim(),
      phoneNumber: _phone.text.trim(),
      emailAddress: _email.text.trim(),
      preferredLanguage: scope.locale.languageCode,
      city: _city,
    );
    if (!mounted) return;
    setState(() => _loading = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(tr(context, en: 'Profile updated.', ar: 'تم تحديث الملف الشخصي.'))));
    Navigator.pop(context, true);
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    final cities = store.availableCities.isEmpty ? const ['Salalah', 'Muscat', 'Seeb'] : store.availableCities;
    return Scaffold(
      appBar: AppBar(title: Text(tr(context, en: 'Edit profile', ar: 'تعديل الملف الشخصي'))),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          NeoCard(
            child: Column(
              children: [
                AppTextField(
                  hint: tr(context, en: 'Full name', ar: 'الاسم الكامل'),
                  controller: _name,
                  prefixIcon: Icons.badge_outlined,
                ),
                const SizedBox(height: 12),
                AppTextField(
                  hint: tr(context, en: 'Phone number', ar: 'رقم الهاتف'),
                  controller: _phone,
                  keyboardType: TextInputType.phone,
                  prefixIcon: Icons.phone_outlined,
                ),
                const SizedBox(height: 12),
                AppTextField(
                  hint: tr(context, en: 'Email', ar: 'البريد الإلكتروني'),
                  controller: _email,
                  keyboardType: TextInputType.emailAddress,
                  prefixIcon: Icons.mail_outline_rounded,
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: _city,
                  decoration: InputDecoration(
                    hintText: tr(context, en: 'Preferred city', ar: 'المدينة المفضلة'),
                    prefixIcon: const Icon(Icons.location_city_outlined),
                  ),
                  items: cities
                      .map((city) => DropdownMenuItem<String>(
                            value: city,
                            child: Text(cityLabel(context, city)),
                          ))
                      .toList(),
                  onChanged: (value) {
                    if (value == null) return;
                    setState(() => _city = value);
                  },
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _loading ? null : _save,
                  child: _loading
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : Text(tr(context, en: 'Save changes', ar: 'حفظ التغييرات')),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
