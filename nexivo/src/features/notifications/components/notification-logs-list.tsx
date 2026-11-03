import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { notificationLogs } from "@/features/notifications/data/notification-data";
import {
  getNotificationChannelIcon,
  getNotificationChannelLabel
} from "@/features/notifications/components/notification-utils";

export function NotificationLogsList() {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Notification Logs</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Delivery logs prepared for email, SMS, WhatsApp, and push notification integrations.
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {notificationLogs.map((log) => {
          const Icon = getNotificationChannelIcon(log.channel);

          return (
            <div
              key={log.id}
              className="flex flex-col gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft md:flex-row md:items-center md:justify-between"
            >
              <div className="flex gap-4">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                  <Icon size={21} />
                </div>

                <div>
                  <h3 className="font-heading text-lg font-semibold text-luxury-ink">
                    {log.title}
                  </h3>
                  <p className="mt-1 text-sm text-slate-600">{log.description}</p>
                  <p className="mt-1 text-xs font-bold uppercase tracking-[0.14em] text-slate-400">
                    {getNotificationChannelLabel(log.channel)} • {log.recipient} • {log.createdAt}
                  </p>
                </div>
              </div>

              <Badge
                variant={
                  log.status === "sent"
                    ? "success"
                    : log.status === "pending"
                      ? "warning"
                      : "destructive"
                }
              >
                {log.status}
              </Badge>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
