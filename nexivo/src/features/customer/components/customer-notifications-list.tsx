import { Bell, Mail, MessageCircle, Smartphone } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CustomerNotification } from "@/features/customer/types/customer.types";

type CustomerNotificationsListProps = {
  notifications: CustomerNotification[];
};

export function CustomerNotificationsList({ notifications }: CustomerNotificationsListProps) {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Notification Center</CardTitle>
        <p className="text-sm text-slate-600">
          Prepared for email, SMS, WhatsApp, and push notification workflows.
        </p>
      </CardHeader>

      <CardContent className="space-y-3">
        {notifications.map((notification) => {
          const Icon =
            notification.channel === "email"
              ? Mail
              : notification.channel === "whatsapp"
                ? MessageCircle
                : notification.channel === "sms"
                  ? Smartphone
                  : Bell;

          return (
            <div
              key={notification.id}
              className="flex gap-4 rounded-3xl border border-slate-200 bg-white p-4 shadow-soft"
            >
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-brand-50 text-brand-700">
                <Icon size={19} />
              </div>

              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className="font-semibold text-luxury-ink">{notification.title}</h3>
                  <Badge variant={notification.read ? "secondary" : "success"}>
                    {notification.read ? "Read" : "New"}
                  </Badge>
                </div>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  {notification.description}
                </p>
                <p className="mt-2 text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
                  {notification.channel} • {notification.date}
                </p>
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
