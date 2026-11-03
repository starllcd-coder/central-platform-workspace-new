import 'package:flutter/material.dart';

import '../../core/utils/tr.dart';
import '../../core/widgets/app_text_field.dart';
import '../../core/widgets/gradient_scaffold.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final phoneCtrl = TextEditingController();
  final otpCtrl = TextEditingController();
  final passwordCtrl = TextEditingController();
  bool sent = false;
  bool loading = false;

  @override
  void dispose() {
    phoneCtrl.dispose();
    otpCtrl.dispose();
    passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _send() async {
    setState(() => loading = true);
    final store = LaundrexScope.of(context).store;
    final message = await store.sendResetOtp(phoneCtrl.text.trim());
    if (!mounted) return;
    setState(() => loading = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
    } else {
      setState(() => sent = true);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(tr(context, en: 'Reset code sent.', ar: 'تم إرسال رمز إعادة التعيين.'))));
    }
  }

  Future<void> _reset() async {
    setState(() => loading = true);
    final store = LaundrexScope.of(context).store;
    final message = await store.resetPassword(
      phoneNumber: phoneCtrl.text.trim(),
      code: otpCtrl.text.trim(),
      newPassword: passwordCtrl.text,
    );
    if (!mounted) return;
    setState(() => loading = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(tr(context, en: 'Password updated.', ar: 'تم تحديث كلمة المرور.'))));
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return GradientScaffold(
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.arrow_back_ios_new_rounded)),
            const SizedBox(height: 12),
            Text(tr(context, en: 'Reset password', ar: 'إعادة تعيين كلمة المرور'), style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text(tr(context, en: 'We will send an OTP to reset your password.', ar: 'سنرسل رمز تحقق لإعادة تعيين كلمة المرور.'), style: Theme.of(context).textTheme.bodyLarge),
            const SizedBox(height: 24),
            NeoCard(
              child: Column(
                children: [
                  AppTextField(hint: tr(context, en: 'Phone number', ar: 'رقم الهاتف'), controller: phoneCtrl, prefixIcon: Icons.phone_outlined),
                  const SizedBox(height: 16),
                  if (!sent)
                    ElevatedButton(
                      onPressed: loading ? null : _send,
                      child: loading
                          ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : Text(tr(context, en: 'Send reset code', ar: 'إرسال رمز إعادة التعيين')),
                    ),
                  if (sent) ...[
                    AppTextField(hint: tr(context, en: 'OTP code', ar: 'رمز التحقق'), controller: otpCtrl, prefixIcon: Icons.lock_clock_rounded),
                    const SizedBox(height: 12),
                    AppTextField(hint: tr(context, en: 'New password', ar: 'كلمة المرور الجديدة'), controller: passwordCtrl, obscureText: true, prefixIcon: Icons.lock_outline_rounded),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: loading ? null : _reset,
                      child: loading
                          ? const SizedBox(height: 22, width: 22, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : Text(tr(context, en: 'Reset password', ar: 'إعادة تعيين كلمة المرور')),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
