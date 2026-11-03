import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { notificationTemplates } from "@/features/notifications/data/notification-data";
import {
  getNotificationChannelIcon,
  getNotificationChannelLabel
} from "@/features/notifications/components/notification-utils";

export function NotificationTemplatesGrid() {
  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Notification Templates</CardTitle>
        <p className="text-sm leading-6 text-slate-600">
          Templates are prepared for DSS Central Platform configuration and future provider-specific
          notification rules.
        </p>
      </CardHeader>

      <CardContent className="grid gap-5 lg:grid-cols-2">
        {notificationTemplates.map((template) => (
          <article
            key={template.id}
            className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
          >
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h3 className="font-heading text-xl font-semibold text-luxury-ink">
                  {template.title}
                </h3>
                <p className="mt-1 text-sm text-slate-500">{template.category}</p>
              </div>

              <Badge variant={template.enabled ? "success" : "secondary"}>
                {template.enabled ? "Enabled" : "Disabled"}
              </Badge>
            </div>

            <div className="mt-4 rounded-3xl bg-slate-50 p-4">
              <p className="text-sm font-semibold text-luxury-ink">{template.subject}</p>
              <p className="mt-2 text-sm leading-6 text-slate-600">{template.body}</p>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {template.channels.map((channel) => {
                const Icon = getNotificationChannelIcon(channel);

                return (
                  <Badge key={channel} variant="outline">
                    <Icon className="mr-1" size={13} />
                    {getNotificationChannelLabel(channel)}
                  </Badge>
                );
              })}
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {template.variables.map((variable) => (
                <Badge key={variable} variant="secondary">
                  {`{{${variable}}}`}
                </Badge>
              ))}
            </div>
          </article>
        ))}
      </CardContent>
    </Card>
  );
}
