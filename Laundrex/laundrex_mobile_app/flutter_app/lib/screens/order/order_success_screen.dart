import 'package:flutter/material.dart';

import '../../core/utils/app_navigator.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/gradient_scaffold.dart';
import '../../main.dart';
import '../home/app_shell.dart';
import 'receipt_screen.dart';

class OrderSuccessScreen extends StatelessWidget {
  const OrderSuccessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    return GradientScaffold(
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(22),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 92,
                height: 92,
                decoration: BoxDecoration(
                  color: const Color(0xFF22C55E),
                  borderRadius: BorderRadius.circular(30),
                ),
                child: const Icon(Icons.check_rounded, size: 52, color: Colors.white),
              ),
              const SizedBox(height: 18),
              Text(
                tr(context, en: 'Order placed successfully', ar: 'تم إنشاء الطلب بنجاح'),
                style: Theme.of(context).textTheme.headlineMedium,
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 10),
              Text(
                tr(
                  context,
                  en: 'Your pickup request has been sent to the laundry.',
                  ar: 'تم إرسال طلب الاستلام إلى المغسلة.',
                ),
                textAlign: TextAlign.center,
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(color: Colors.black54),
              ),
              const SizedBox(height: 24),
              if (store.lastReceipt != null) ...[
                OutlinedButton.icon(
                  onPressed: () => AppNavigator.push(context, const ReceiptScreen()),
                  icon: const Icon(Icons.receipt_long_outlined),
                  label: Text(tr(context, en: 'View receipt', ar: 'عرض الإيصال')),
                ),
                const SizedBox(height: 12),
              ],
              ElevatedButton(
                onPressed: () => AppNavigator.replace(context, const AppShell()),
                child: Text(tr(context, en: 'Back to home', ar: 'العودة للرئيسية')),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
