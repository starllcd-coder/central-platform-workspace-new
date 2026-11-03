import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../data/mock_store.dart';
import '../../main.dart';

class OrderTrackingScreen extends StatefulWidget {
  const OrderTrackingScreen({super.key, required this.orderId, required this.orderCode, required this.status});

  final int? orderId;
  final String orderCode;
  final String status;

  @override
  State<OrderTrackingScreen> createState() => _OrderTrackingScreenState();
}

class _OrderTrackingScreenState extends State<OrderTrackingScreen> {
  Timer? _timer;
  bool cancelling = false;
  bool loading = true;
  String currentStatus = '';
  String etaLabel = '';
  List<TrackingEvent> events = [];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _loadTracking());
    _timer = Timer.periodic(const Duration(seconds: 15), (_) => _loadTracking(silent: true));
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    final status = (currentStatus.isEmpty ? widget.status : currentStatus).toUpperCase();
    final canCancel = widget.orderId != null && status != 'DELIVERED' && status != 'CANCELLED';

    return Scaffold(
      appBar: AppBar(title: Text(widget.orderCode)),
      body: ListView(
        padding: const EdgeInsets.all(18),
        children: [
          NeoCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  tr(context, en: 'Order tracking', ar: 'تتبع الطلب'),
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800),
                ),
                const SizedBox(height: 6),
                Text(
                  etaLabel.isEmpty ? store.getEtaLabel(widget.status) : etaLabel,
                  style: Theme.of(context).textTheme.bodyMedium,
                ),
                if (canCancel) ...[
                  const SizedBox(height: 12),
                  OutlinedButton.icon(
                    onPressed: cancelling
                        ? null
                        : () async {
                            setState(() => cancelling = true);
                            final message = await store.cancelOrder(widget.orderId!);
                            if (!context.mounted) return;
                            setState(() => cancelling = false);
                            if (message != null) {
                              ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
                            } else {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(content: Text(tr(context, en: 'Order cancelled.', ar: 'تم إلغاء الطلب.'))),
                              );
                              Navigator.pop(context);
                            }
                          },
                    icon: cancelling
                        ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                        : const Icon(Icons.cancel_outlined),
                    label: Text(tr(context, en: 'Cancel order', ar: 'إلغاء الطلب')),
                  ),
                ],
                const SizedBox(height: 18),
                if (loading)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 20),
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  )
                else
                  ...List.generate(events.length, (index) {
                    final event = events[index];
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Column(
                          children: [
                            Container(
                              width: 20,
                              height: 20,
                              decoration: BoxDecoration(
                                color: event.completed ? AppColors.primary : Colors.grey.shade300,
                                shape: BoxShape.circle,
                              ),
                            ),
                            if (index != events.length - 1)
                              Container(
                                width: 2,
                                height: 42,
                                color: event.completed ? AppColors.primary : Colors.grey.shade300,
                              ),
                          ],
                        ),
                        const SizedBox(width: 14),
                        Padding(
                          padding: const EdgeInsets.only(top: 1),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                event.label,
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                  color: event.completed ? null : Colors.grey,
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                event.time == null
                                    ? tr(context, en: 'Pending', ar: 'قيد الانتظار')
                                    : '${tr(context, en: 'Updated', ar: 'آخر تحديث')} ${_formatTime(event.time!)}',
                                style: Theme.of(context).textTheme.bodyMedium,
                              ),
                            ],
                          ),
                        ),
                      ],
                    );
                  }),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _loadTracking({bool silent = false}) async {
    if (!mounted) return;
    if (!silent) {
      setState(() => loading = true);
    }
    final store = LaundrexScope.of(context).store;
    final snapshot = await store.fetchOrderTracking(
      orderId: widget.orderId,
      orderCode: widget.orderCode,
      fallbackStatus: widget.status,
    );
    if (!mounted) return;
    setState(() {
      currentStatus = snapshot.status;
      etaLabel = snapshot.eta;
      events = snapshot.events;
      loading = false;
    });
  }

  String _formatTime(DateTime time) {
    final h = time.hour.toString().padLeft(2, '0');
    final m = time.minute.toString().padLeft(2, '0');
    return '$h:$m';
  }
}
