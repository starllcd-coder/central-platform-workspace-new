import { Bell, Mail, MessageCircle, Smartphone } from "lucide-react";
import type { NotificationChannel } from "@/features/notifications/types/notification.types";

export function getNotificationChannelIcon(channel: NotificationChannel) {
  const map = {
    email: Mail,
    sms: Smartphone,
    whatsapp: MessageCircle,
    push: Bell
  };

  return map[channel];
}

export function getNotificationChannelLabel(channel: NotificationChannel) {
  const map = {
    email: "Email",
    sms: "SMS",
    whatsapp: "WhatsApp",
    push: "Push"
  };

  return map[channel];
}
