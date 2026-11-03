export type NotificationChannel = "email" | "sms" | "whatsapp" | "push";

export type NotificationCategory =
  | "booking"
  | "payment"
  | "reminder"
  | "promotion"
  | "security"
  | "business";

export type NotificationTemplate = {
  id: string;
  title: string;
  category: NotificationCategory;
  channels: NotificationChannel[];
  subject: string;
  body: string;
  variables: string[];
  enabled: boolean;
};

export type NotificationPreference = {
  channel: NotificationChannel;
  enabled: boolean;
  bookingUpdates: boolean;
  paymentUpdates: boolean;
  reminders: boolean;
  promotions: boolean;
  securityAlerts: boolean;
  businessUpdates: boolean;
};

export type NotificationLog = {
  id: string;
  title: string;
  description: string;
  category: NotificationCategory;
  channel: NotificationChannel;
  recipient: string;
  status: "sent" | "pending" | "failed";
  createdAt: string;
};
