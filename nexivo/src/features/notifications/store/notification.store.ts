"use client";

import { create } from "zustand";
import type {
  NotificationChannel,
  NotificationPreference
} from "@/features/notifications/types/notification.types";
import { defaultNotificationPreferences } from "@/features/notifications/data/notification-data";

type NotificationStore = {
  preferences: NotificationPreference[];
  toggleChannel: (channel: NotificationChannel) => void;
  updatePreference: (
    channel: NotificationChannel,
    key: keyof Omit<NotificationPreference, "channel">,
    value: boolean
  ) => void;
  resetPreferences: () => void;
};

export const useNotificationStore = create<NotificationStore>((set) => ({
  preferences: defaultNotificationPreferences,

  toggleChannel: (channel) =>
    set((state) => ({
      preferences: state.preferences.map((preference) =>
        preference.channel === channel
          ? { ...preference, enabled: !preference.enabled }
          : preference
      )
    })),

  updatePreference: (channel, key, value) =>
    set((state) => ({
      preferences: state.preferences.map((preference) =>
        preference.channel === channel ? { ...preference, [key]: value } : preference
      )
    })),

  resetPreferences: () => set({ preferences: defaultNotificationPreferences })
}));
