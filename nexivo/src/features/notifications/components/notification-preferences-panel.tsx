"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useNotificationStore } from "@/features/notifications/store/notification.store";
import {
  getNotificationChannelIcon,
  getNotificationChannelLabel
} from "@/features/notifications/components/notification-utils";

const preferenceKeys = [
  ["bookingUpdates", "Booking updates"],
  ["paymentUpdates", "Payment updates"],
  ["reminders", "Reminders"],
  ["promotions", "Promotions"],
  ["securityAlerts", "Security alerts"],
  ["businessUpdates", "Business updates"]
] as const;

export function NotificationPreferencesPanel() {
  const { preferences, toggleChannel, updatePreference, resetPreferences } =
    useNotificationStore();

  return (
    <Card variant="premium">
      <CardHeader>
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <CardTitle>Notification Preferences</CardTitle>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Configure how Nexivo sends booking, payment, reminder, promotional, security, and
              business updates.
            </p>
          </div>

          <Button variant="outline" onClick={resetPreferences}>
            Reset
          </Button>
        </div>
      </CardHeader>

      <CardContent className="grid gap-5 lg:grid-cols-2">
        {preferences.map((preference) => {
          const Icon = getNotificationChannelIcon(preference.channel);

          return (
            <div
              key={preference.channel}
              className="rounded-4xl border border-slate-200 bg-white p-5 shadow-soft"
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                    <Icon size={21} />
                  </div>

                  <div>
                    <h3 className="font-heading text-xl font-semibold text-luxury-ink">
                      {getNotificationChannelLabel(preference.channel)}
                    </h3>
                    <p className="text-sm text-slate-500">
                      {preference.enabled ? "Enabled" : "Disabled"}
                    </p>
                  </div>
                </div>

                <label className="relative inline-flex cursor-pointer items-center">
                  <input
                    type="checkbox"
                    checked={preference.enabled}
                    onChange={() => toggleChannel(preference.channel)}
                    className="peer sr-only"
                  />
                  <span className="h-7 w-12 rounded-full bg-slate-200 after:absolute after:left-1 after:top-1 after:h-5 after:w-5 after:rounded-full after:bg-white after:transition-all peer-checked:bg-brand-600 peer-checked:after:translate-x-5" />
                </label>
              </div>

              <div className="mt-5 space-y-3">
                {preferenceKeys.map(([key, label]) => (
                  <label
                    key={key}
                    className="flex items-center justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3 text-sm font-medium text-slate-700"
                  >
                    <span>{label}</span>
                    <input
                      type="checkbox"
                      checked={Boolean(preference[key])}
                      disabled={!preference.enabled}
                      onChange={(event) =>
                        updatePreference(preference.channel, key, event.target.checked)
                      }
                      className="h-4 w-4 rounded border-slate-300 text-brand-600 disabled:opacity-40"
                    />
                  </label>
                ))}
              </div>
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}
