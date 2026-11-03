import 'package:flutter/material.dart';

import '../../core/theme/app_theme.dart';
import '../../core/utils/tr.dart';
import '../../core/widgets/neo_card.dart';
import '../../main.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  bool loading = true;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _load());
  }

  Future<void> _load() async {
    await LaundrexScope.of(context).store.fetchNotifications();
    if (!mounted) return;
    setState(() => loading = false);
  }

  @override
  Widget build(BuildContext context) {
    final store = LaundrexScope.of(context).store;
    return AnimatedBuilder(
      animation: store,
      builder: (context, _) {
        final rows = store.notifications;
        return Scaffold(
          appBar: AppBar(
            title: Text(tr(context, en: 'Notifications', ar: 'الإشعارات')),
            actions: [
              TextButton(
                onPressed: rows.isEmpty
                    ? null
                    : () async {
                        await store.markNotificationsRead();
                      },
                child: Text(tr(context, en: 'Mark all read', ar: 'تحديد الكل كمقروء')),
              ),
            ],
          ),
          body: loading
              ? const Center(child: CircularProgressIndicator(strokeWidth: 2))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.separated(
                    padding: const EdgeInsets.all(18),
                    itemCount: rows.isEmpty ? 1 : rows.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 12),
                    itemBuilder: (context, index) {
                      if (rows.isEmpty) {
                        return NeoCard(
                          child: Text(tr(context, en: 'No notifications yet.', ar: 'لا توجد إشعارات بعد.')),
                        );
                      }
                      final item = rows[index];
                      return GestureDetector(
                        onTap: () async {
                          if (!item.isRead) {
                            await store.markNotificationsRead(id: item.id);
                          }
                        },
                        child: NeoCard(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      item.title,
                                      style: TextStyle(
                                        fontWeight: item.isRead ? FontWeight.w700 : FontWeight.w800,
                                        fontSize: 16,
                                      ),
                                    ),
                                  ),
                                  if (!item.isRead)
                                    Container(
                                      width: 10,
                                      height: 10,
                                      decoration: const BoxDecoration(
                                        color: AppColors.primary,
                                        shape: BoxShape.circle,
                                      ),
                                    ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              Text(item.message),
                              if (item.orderNo.isNotEmpty) ...[
                                const SizedBox(height: 6),
                                Text(
                                  '${tr(context, en: 'Order', ar: 'الطلب')} #${item.orderNo}',
                                  style: Theme.of(context).textTheme.bodyMedium,
                                ),
                              ],
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
        );
      },
    );
  }
}
