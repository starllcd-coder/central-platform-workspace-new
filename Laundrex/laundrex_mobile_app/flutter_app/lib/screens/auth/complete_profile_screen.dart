import 'package:flutter/material.dart';

import '../../core/utils/app_navigator.dart';
import '../../core/utils/city_names.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/gradient_scaffold.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';
import '../home/app_shell.dart';

class CompleteProfileScreen extends StatefulWidget {
  const CompleteProfileScreen({super.key});

  @override
  State<CompleteProfileScreen> createState() => _CompleteProfileScreenState();
}

class _CompleteProfileScreenState extends State<CompleteProfileScreen> {
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  bool _saving = false;
  String _selectedCity = 'Salalah';
  bool _initialized = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_initialized) return;
    _initialized = true;
    final store = LaundrexScope.of(context).store;
    _nameController.text = store.userName == 'Customer' || store.userName == 'Guest' ? '' : store.userName;
    _emailController.text = store.email;
    final cities = store.availableCities;
    if (cities.isNotEmpty) {
      _selectedCity = cities.contains(store.selectedCity) ? store.selectedCity : cities.first;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final store = LaundrexScope.of(context).store;
    setState(() => _saving = true);
    final message = await store.completeProfileAfterOtp(
      fullName: _nameController.text,
      city: _selectedCity,
      emailAddress: _emailController.text,
    );
    if (!mounted) return;
    setState(() => _saving = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      return;
    }
    AppNavigator.replace(context, const AppShell());
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    final cities = store.availableCities.isEmpty ? const ['Salalah', 'Muscat', 'Seeb'] : store.availableCities;
    if (!cities.contains(_selectedCity)) {
      _selectedCity = cities.first;
    }
    return GradientScaffold(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(22),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: NeoCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(tr(context, en: 'Complete your profile', ar: 'أكمل ملفك الشخصي'), style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 8),
                  Text(tr(context, en: 'After OTP verification, set your details to continue.', ar: 'بعد التحقق من الرمز، أدخل بياناتك للمتابعة.'), style: Theme.of(context).textTheme.bodyLarge),
                  const SizedBox(height: 14),
                  TextField(
                    controller: _nameController,
                    decoration: InputDecoration(
                      hintText: tr(context, en: 'Full name', ar: 'الاسم الكامل'),
                      prefixIcon: const Icon(Icons.badge_outlined),
                    ),
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    initialValue: _selectedCity,
                    decoration: InputDecoration(
                      hintText: tr(context, en: 'Preferred city', ar: 'المدينة المفضلة'),
                      prefixIcon: const Icon(Icons.location_city_outlined),
                    ),
                    items: cities
                        .map((city) => DropdownMenuItem<String>(value: city, child: Text(cityLabel(context, city))))
                        .toList(),
                    onChanged: (value) {
                      if (value == null) return;
                      setState(() => _selectedCity = value);
                    },
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: InputDecoration(
                      hintText: tr(context, en: 'Email (optional)', ar: 'البريد الإلكتروني (اختياري)'),
                      prefixIcon: const Icon(Icons.mail_outline),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _saving ? null : _save,
                    child: _saving
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          )
                        : Text(tr(context, en: 'Continue', ar: 'متابعة')),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
