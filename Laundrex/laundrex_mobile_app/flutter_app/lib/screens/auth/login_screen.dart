import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/app_text_field.dart';
import '../../core/widgets/brand_logo.dart';
import '../../core/widgets/glass_card.dart';
import '../../core/widgets/gradient_scaffold.dart';
import '../../main.dart';
import '../home/app_shell.dart';
import 'forgot_password_screen.dart';
import 'phone_login_screen.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _userController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _loading = false;
  bool _showPassword = false;
  bool _prefilledUser = false;
  bool _rememberMe = true;
  bool _retryingConnection = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_prefilledUser) return;
    _prefilledUser = true;
    final store = LaundrexScope.of(context).store;
    if (_userController.text.trim().isNotEmpty) return;
    _rememberMe = store.rememberMe;
    if (store.phone.trim().isNotEmpty && store.phone != '+968 9000 0000') {
      _userController.text = store.phone;
    }
  }

  @override
  void dispose() {
    _userController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    setState(() => _loading = true);
    final store = LaundrexScope.of(context).store;
    await store.setRememberMe(_rememberMe);
    final message = await store.loginRemote(
      username: _userController.text.trim(),
      password: _passwordController.text,
    );
    if (!mounted) return;
    setState(() => _loading = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
    }
    if (store.isLoggedIn) {
      AppNavigator.replace(context, const AppShell());
    }
  }

  Future<Map<String, String>?> _promptSocialInfo() async {
    final emailCtrl = TextEditingController();
    final nameCtrl = TextEditingController();
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(tr(context, en: 'Continue with social login', ar: 'المتابعة عبر تسجيل الدخول الاجتماعي')),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: emailCtrl, decoration: InputDecoration(hintText: tr(context, en: 'Email', ar: 'البريد الإلكتروني'))),
            const SizedBox(height: 12),
            TextField(controller: nameCtrl, decoration: InputDecoration(hintText: tr(context, en: 'Full name (optional)', ar: 'الاسم الكامل (اختياري)'))),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: Text(tr(context, en: 'Cancel', ar: 'إلغاء'))),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, {
              'email': emailCtrl.text.trim(),
              'name': nameCtrl.text.trim(),
            }),
            child: Text(tr(context, en: 'Continue', ar: 'متابعة')),
          ),
        ],
      ),
    );
    return result;
  }

  Future<void> _socialLogin(String provider) async {
    final info = await _promptSocialInfo();
    if (!mounted || info == null) return;
    final email = info['email'] ?? '';
    if (email.isEmpty) return;
    setState(() => _loading = true);
    final store = LaundrexScope.of(context).store;
    final message = await store.socialLogin(provider: provider, email: email, fullName: info['name'] ?? '');
    if (!mounted) return;
    setState(() => _loading = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
    }
    if (store.isLoggedIn) {
      AppNavigator.replace(context, const AppShell());
    }
  }

  Future<void> _retryConnection() async {
    setState(() => _retryingConnection = true);
    final store = LaundrexScope.of(context).store;
    final ok = await store.retryPublicConnection();
    if (!mounted) return;
    setState(() => _retryingConnection = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok
              ? tr(context, en: 'Connection restored. Please login again.', ar: 'تمت استعادة الاتصال. يرجى تسجيل الدخول مرة أخرى.')
              : tr(context, en: 'Could not reach server. Please try again.', ar: 'تعذر الوصول إلى الخادم. يرجى المحاولة مرة أخرى.'),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final scope = LaundrexScope.of(context);
    final store = scope.store;
    final isArabic = isArabicLocale(context);
    final sessionExpiredTitle = tr(context, en: 'Session expired. Please login again.', ar: 'انتهت الجلسة. يرجى تسجيل الدخول مرة أخرى.');
    final retryLabel = tr(context, en: 'Retry connection', ar: 'إعادة المحاولة');
    final dismissLabel = tr(context, en: 'Dismiss', ar: 'إغلاق');

    return GradientScaffold(
      child: SingleChildScrollView(
        padding: const EdgeInsets.fromLTRB(22, 18, 22, 28),
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 380),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                Align(
                  alignment: Alignment.centerRight,
                  child: GestureDetector(
                    onTap: () => scope.setLocale(isArabic ? const Locale('en') : const Locale('ar')),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFFE6EEF9)),
                        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: .05), blurRadius: 10, offset: const Offset(0, 6))],
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Text(isArabic ? 'AR' : 'EN', style: const TextStyle(fontWeight: FontWeight.w700)),
                          const SizedBox(width: 6),
                          const Icon(Icons.keyboard_arrow_down_rounded, size: 18),
                        ],
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Hero(
                  tag: 'laundrex-logo',
                  child: BrandLogo(
                    size: MediaQuery.sizeOf(context).width < 400 ? 140 : 156,
                    cropFactor: 0.82,
                    useSvg: false,
                  ),
                ),
                const SizedBox(height: 10),
                Text(tr(context, en: 'Smart Laundry. Simplified.', ar: 'غسيل ذكي. ببساطة.'), style: Theme.of(context).textTheme.bodyMedium),
                const SizedBox(height: 14),
                Text(tr(context, en: 'Welcome Back', ar: 'مرحبًا بعودتك'), style: Theme.of(context).textTheme.headlineMedium),
                const SizedBox(height: 6),
                Text(tr(context, en: 'Please login to your account', ar: 'يرجى تسجيل الدخول إلى حسابك'), style: Theme.of(context).textTheme.bodyLarge),
                if (store.sessionExpired) ...[
                  const SizedBox(height: 12),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: const Color(0xFFFFF7ED),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFFED7AA)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.info_outline_rounded, size: 18, color: Color(0xFF9A3412)),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                sessionExpiredTitle,
                                style: const TextStyle(fontWeight: FontWeight.w700, color: Color(0xFF9A3412)),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: [
                            OutlinedButton.icon(
                              onPressed: _retryingConnection ? null : _retryConnection,
                              icon: _retryingConnection
                                  ? const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2))
                                  : const Icon(Icons.refresh_rounded, size: 16),
                              label: Text(retryLabel),
                            ),
                            const SizedBox(width: 8),
                            TextButton(
                              onPressed: () {
                                store.clearSessionExpiredFlag();
                                setState(() {});
                              },
                              child: Text(dismissLabel),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 22),
                GlassCard(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    children: [
                      AppTextField(
                        hint: tr(context, en: 'Phone number or email', ar: 'رقم الهاتف أو البريد الإلكتروني'),
                        controller: _userController,
                        prefixIcon: Icons.person_outline_rounded,
                        suffixIcon: Icons.check_circle_rounded,
                        suffixColor: const Color(0xFF22C55E),
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        hint: tr(context, en: 'Password', ar: 'كلمة المرور'),
                        controller: _passwordController,
                        obscureText: !_showPassword,
                        prefixIcon: Icons.lock_outline_rounded,
                        suffixIcon: _showPassword ? Icons.visibility_off_outlined : Icons.visibility_outlined,
                        suffixColor: const Color(0xFF8CA0BF),
                        onSuffixTap: () => setState(() => _showPassword = !_showPassword),
                      ),
                      Align(
                        alignment: Alignment.centerRight,
                        child: TextButton(
                          onPressed: () => AppNavigator.push(context, const ForgotPasswordScreen()),
                          child: Text(tr(context, en: 'Forgot Password?', ar: 'هل نسيت كلمة المرور؟')),
                        ),
                      ),
                      Row(
                        children: [
                          Checkbox(
                            value: _rememberMe,
                            onChanged: (value) {
                              if (value == null) return;
                              setState(() => _rememberMe = value);
                              store.setRememberMe(value);
                            },
                          ),
                          Text(tr(context, en: 'Remember me', ar: 'تذكرني')),
                        ],
                      ),
                      const SizedBox(height: 8),
                      AnimatedScale(
                        duration: const Duration(milliseconds: 180),
                        scale: _loading ? .98 : 1,
                        child: Container(
                          width: double.infinity,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(colors: [AppColors.primaryDeep, AppColors.primary]),
                            borderRadius: BorderRadius.circular(14),
                            boxShadow: const [BoxShadow(color: Color(0x33134B8A), blurRadius: 18, offset: Offset(0, 10))],
                          ),
                          child: ElevatedButton(
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.transparent,
                              shadowColor: Colors.transparent,
                              minimumSize: const Size(double.infinity, 50),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                            ),
                            onPressed: _loading ? null : _login,
                            child: _loading
                                ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                                : Text(tr(context, en: 'Login', ar: 'تسجيل الدخول')),
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      OutlinedButton.icon(
                        onPressed: () => AppNavigator.push(context, const PhoneLoginScreen()),
                        icon: const Icon(Icons.sms_outlined),
                        label: Text(tr(context, en: 'Login with phone number', ar: 'تسجيل الدخول برقم الهاتف')),
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          const Expanded(child: Divider(thickness: 1, color: Color(0xFFE6EEF9))),
                          Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 10),
                            child: Text(tr(context, en: 'Or continue with', ar: 'أو المتابعة عبر'), style: const TextStyle(color: Color(0xFF7B8BA3))),
                          ),
                          const Expanded(child: Divider(thickness: 1, color: Color(0xFFE6EEF9))),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: store.googleEnabled && !_loading ? () => _socialLogin('google') : null,
                              icon: const Icon(Icons.g_mobiledata_rounded),
                              label: Text(tr(context, en: 'Google', ar: 'جوجل')),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: OutlinedButton.icon(
                              onPressed: store.appleEnabled && !_loading ? () => _socialLogin('apple') : null,
                              icon: const Icon(Icons.apple),
                              label: Text(tr(context, en: 'Apple', ar: 'آبل')),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                Wrap(
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Text(tr(context, en: 'Don\'t have an account? ', ar: 'ليس لديك حساب؟ '), style: const TextStyle(color: Color(0xFF7B8BA3))),
                    TextButton(
                      onPressed: () => AppNavigator.push(context, const RegisterScreen()),
                      child: Text(tr(context, en: 'Sign up', ar: 'إنشاء حساب')),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
