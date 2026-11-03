import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/city_names.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/app_text_field.dart';
import '../../core/widgets/gradient_scaffold.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';
import '../home/app_shell.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final name = TextEditingController();
  final phone = TextEditingController();
  final email = TextEditingController();
  final password = TextEditingController();
  String selectedCity = 'Salalah';
  bool loading = false;

  @override
  void dispose() {
    name.dispose();
    phone.dispose();
    email.dispose();
    password.dispose();
    super.dispose();
  }

  Future<void> submit() async {
    setState(() => loading = true);
    final store = LaundrexScope.of(context).store;
    final message = await store.registerRemote(
      fullName: name.text.trim().isEmpty ? 'New Customer' : name.text.trim(),
      phoneNumber: phone.text.trim(),
      email: email.text.trim(),
      password: password.text,
      city: selectedCity,
    );
    if (!mounted) return;
    setState(() => loading = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
    }
    if (store.isLoggedIn) {
      AppNavigator.replace(context, const AppShell());
    }
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    final cities = store.availableCities.isEmpty ? const ['Salalah', 'Muscat', 'Seeb'] : store.availableCities;
    if (!cities.contains(selectedCity)) {
      selectedCity = cities.first;
    }
    return GradientScaffold(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(22),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    IconButton(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back_ios_new_rounded),
                    ),
                    const SizedBox(width: 6),
                    Text(tr(context, en: 'Create Account', ar: 'إنشاء حساب'), style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
                  ],
                ),
                const SizedBox(height: 16),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    color: const Color(0xFFEFF5FF),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(tr(context, en: 'Set up your customer profile', ar: 'إعداد ملفك الشخصي'), style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 8),
                      Text(tr(context, en: 'Fast booking, saved addresses, and order tracking all start here.', ar: 'الحجز السريع، العناوين المحفوظة، وتتبع الطلبات يبدأ من هنا.'), style: Theme.of(context).textTheme.bodyLarge),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                NeoCard(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(tr(context, en: 'Account Details', ar: 'تفاصيل الحساب'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 18)),
                      const SizedBox(height: 16),
                      AppTextField(hint: tr(context, en: 'Full name', ar: 'الاسم الكامل'), controller: name, prefixIcon: Icons.badge_outlined),
                      const SizedBox(height: 12),
                      AppTextField(hint: tr(context, en: 'Phone number', ar: 'رقم الهاتف'), controller: phone, prefixIcon: Icons.phone_outlined, keyboardType: TextInputType.phone),
                      const SizedBox(height: 12),
                      DropdownButtonFormField<String>(
                        initialValue: selectedCity,
                        decoration: InputDecoration(
                          hintText: tr(context, en: 'City', ar: 'المدينة'),
                          prefixIcon: const Icon(Icons.location_city_outlined),
                        ),
                        icon: const Icon(Icons.keyboard_arrow_down_rounded),
                        isExpanded: true,
                        items: cities
                            .map(
                              (city) => DropdownMenuItem<String>(
                                value: city,
                                child: Text(cityLabel(context, city)),
                              ),
                            )
                            .toList(),
                        onChanged: (value) {
                          if (value == null) return;
                          setState(() => selectedCity = value);
                        },
                      ),
                      const SizedBox(height: 12),
                      AppTextField(hint: tr(context, en: 'Email (optional)', ar: 'البريد الإلكتروني (اختياري)'), controller: email, prefixIcon: Icons.mail_outline_rounded, keyboardType: TextInputType.emailAddress),
                      const SizedBox(height: 12),
                      AppTextField(hint: tr(context, en: 'Password', ar: 'كلمة المرور'), controller: password, prefixIcon: Icons.lock_outline_rounded, obscureText: true),
                      const SizedBox(height: 18),
                      ElevatedButton(
                        onPressed: loading ? null : submit,
                        child: loading
                            ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : Text(tr(context, en: 'Create account', ar: 'إنشاء الحساب')),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
