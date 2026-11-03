import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/gradient_scaffold.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';
import 'complete_profile_screen.dart';
import '../home/app_shell.dart';

class OtpScreen extends StatefulWidget {
  const OtpScreen({
    super.key,
    required this.phoneHint,
    this.requireProfileSetup = false,
  });

  final String phoneHint;
  final bool requireProfileSetup;

  @override
  State<OtpScreen> createState() => _OtpScreenState();
}

class _OtpScreenState extends State<OtpScreen> {
  final List<TextEditingController> ctrls = List.generate(6, (_) => TextEditingController());
  bool loading = false;

  @override
  void dispose() {
    for (final c in ctrls) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> verify() async {
    final code = ctrls.map((e) => e.text).join();
    if (code.length != 6 || !RegExp(r'^\d{6}$').hasMatch(code)) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(tr(context, en: 'Enter the 6-digit OTP code.', ar: 'أدخل رمز التحقق المكون من 6 أرقام.'))));
      return;
    }
    setState(() => loading = true);
    final store = LaundrexScope.of(context).store;
    final message = await store.verifyOtp(code);
    if (!mounted) return;
    setState(() => loading = false);
    if (message != null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
    }
    if (store.isLoggedIn) {
      if (widget.requireProfileSetup) {
        AppNavigator.replace(context, const CompleteProfileScreen());
      } else {
        AppNavigator.replace(context, const AppShell());
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final debugCode = LaundrexScope.of(context).store.lastOtpDebugCode;
    return GradientScaffold(
      child: Padding(
        padding: const EdgeInsets.all(22),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.arrow_back_ios_new_rounded)),
            const SizedBox(height: 12),
            Text(tr(context, en: 'Verify OTP', ar: 'تأكيد رمز التحقق'), style: Theme.of(context).textTheme.headlineMedium),
            const SizedBox(height: 8),
            Text(tr(context, en: 'Enter the code sent to ${widget.phoneHint}.', ar: 'أدخل الرمز المرسل إلى ${widget.phoneHint}.'), style: Theme.of(context).textTheme.bodyLarge),
            if (debugCode != null) ...[
              const SizedBox(height: 8),
              Text('${tr(context, en: 'Debug OTP', ar: 'رمز تجريبي')}: $debugCode', style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.w700)),
            ],
            const SizedBox(height: 24),
            NeoCard(
              child: Column(
                children: [
                  Row(
                    children: List.generate(
                      6,
                      (index) => Expanded(
                        child: Padding(
                          padding: EdgeInsets.only(right: index == 5 ? 0 : 8),
                          child: TextField(
                            controller: ctrls[index],
                            keyboardType: TextInputType.number,
                            textAlign: TextAlign.center,
                            maxLength: 1,
                            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800),
                            decoration: InputDecoration(
                              counterText: '',
                              filled: true,
                              fillColor: AppColors.primarySoft,
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(16),
                                borderSide: const BorderSide(color: AppColors.border),
                              ),
                              enabledBorder: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(16),
                                borderSide: const BorderSide(color: AppColors.border),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: loading ? null : verify,
                    child: loading
                        ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : Text(tr(context, en: 'Verify and continue', ar: 'تأكيد والمتابعة')),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
