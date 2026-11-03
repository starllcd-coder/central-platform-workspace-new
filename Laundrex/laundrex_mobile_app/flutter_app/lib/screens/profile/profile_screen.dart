import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/city_names.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';
import '../address/address_list_screen.dart';
import '../auth/login_screen.dart';
import 'profile_edit_screen.dart';
import '../support/support_screen.dart';
import 'notifications_screen.dart';
import 'wallet_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Future<void> _openEditProfile() async {
    final changed = await AppNavigator.push<bool>(context, const ProfileEditScreen());
    if (!mounted) return;
    if (changed == true) {
      setState(() {});
    }
  }

  Future<void> _deleteAccount() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(tr(context, en: 'Delete account', ar: 'حذف الحساب')),
        content: Text(tr(context, en: 'This will permanently remove your account and data. Continue?', ar: 'سيؤدي هذا إلى حذف حسابك وبياناتك نهائيًا. هل تريد المتابعة؟')),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: Text(tr(context, en: 'Cancel', ar: 'إلغاء'))),
          TextButton(onPressed: () => Navigator.pop(context, true), child: Text(tr(context, en: 'Delete', ar: 'حذف'))),
        ],
      ),
    );
    if (!mounted || confirmed != true) return;
    final store = LaundrexScope.of(context).store;
    final message = await store.deleteAccountRemote();
    if (!mounted) return;
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      return;
    }
    AppNavigator.replace(context, const LoginScreen());
  }

  @override
  Widget build(BuildContext context) {
    final scope = LaundrexScope.of(context);
    final store = scope.store;
    final dark = scope.themeMode == ThemeMode.dark;
    final cities = store.availableCities.isEmpty ? const ['Salalah', 'Muscat', 'Seeb'] : store.availableCities;
    final selectedCity = store.selectedCity.isEmpty ? cities.first : store.selectedCity;
    return Scaffold(
      appBar: AppBar(title: Text(tr(context, en: 'Profile', ar: 'الملف الشخصي'))),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          NeoCard(
            child: Row(
              children: [
                Container(
                  width: 70,
                  height: 70,
                  decoration: BoxDecoration(
                    color: AppColors.primarySoft,
                    borderRadius: BorderRadius.circular(24),
                    border: Border.all(color: AppColors.border),
                  ),
                  child: const Icon(Icons.person_rounded, color: AppColors.primary, size: 36),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(store.userName, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 20)),
                      const SizedBox(height: 6),
                      Text(store.phone),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: _openEditProfile,
                  icon: const Icon(Icons.edit_outlined),
                  tooltip: tr(context, en: 'Edit profile', ar: 'تعديل الملف الشخصي'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          _tile(context, Icons.edit_outlined, tr(context, en: 'Edit profile', ar: 'تعديل الملف الشخصي'), _openEditProfile),
          _tile(context, Icons.location_on_outlined, tr(context, en: 'Saved addresses', ar: 'العناوين المحفوظة'), () => AppNavigator.push(context, const AddressListScreen())),
          _tile(context, Icons.wallet_outlined, tr(context, en: 'Wallet & offers', ar: 'المحفظة والعروض'), () => AppNavigator.push(context, const WalletScreen())),
          _tile(context, Icons.notifications_none_rounded, tr(context, en: 'Notifications', ar: 'الإشعارات'), () => AppNavigator.push(context, const NotificationsScreen())),
          _tile(context, Icons.headset_mic_outlined, tr(context, en: 'Support', ar: 'الدعم'), () => AppNavigator.push(context, const SupportScreen())),
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(context, en: 'Preferred city', ar: 'المدينة المفضلة'), style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  initialValue: cities.contains(selectedCity) ? selectedCity : cities.first,
                  decoration: InputDecoration(
                    hintText: tr(context, en: 'Select city', ar: 'اختر المدينة'),
                    prefixIcon: const Icon(Icons.location_city_outlined),
                  ),
                  items: cities
                      .map((city) => DropdownMenuItem<String>(
                            value: city,
                            child: Text(cityLabel(context, city)),
                          ))
                      .toList(),
                  onChanged: (value) async {
                    if (value == null) return;
                    await store.setSelectedCity(value);
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          NeoCard(
            child: SwitchListTile(
              contentPadding: EdgeInsets.zero,
              value: dark,
              onChanged: (v) => scope.setThemeMode(v ? ThemeMode.dark : ThemeMode.light),
              title: Text(tr(context, en: 'Dark mode', ar: 'الوضع الداكن')),
              subtitle: Text(tr(context, en: 'Elegant low-light appearance', ar: 'مظهر هادئ للإضاءة المنخفضة')),
            ),
          ),
          const SizedBox(height: 14),
          ElevatedButton(
            onPressed: () async {
              await store.logout();
              if (context.mounted) {
                AppNavigator.replace(context, const LoginScreen());
              }
            },
            child: Text(tr(context, en: 'Logout', ar: 'تسجيل الخروج')),
          ),
          const SizedBox(height: 10),
          OutlinedButton(
            onPressed: _deleteAccount,
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.red.shade700,
              side: BorderSide(color: Colors.red.shade200),
            ),
            child: Text(tr(context, en: 'Delete account', ar: 'حذف الحساب')),
          ),
        ],
      ),
    );
  }

  Widget _tile(BuildContext context, IconData icon, String title, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: GestureDetector(
        onTap: onTap,
        child: NeoCard(
          child: Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: AppColors.primarySoft,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppColors.border),
                ),
                child: Icon(icon, color: AppColors.primaryDark, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.w700))),
              const Icon(Icons.chevron_right_rounded, color: AppColors.textMuted),
            ],
          ),
        ),
      ),
    );
  }
}
