import type {
  NotificationLog,
  NotificationPreference,
  NotificationTemplate
} from "@/features/notifications/types/notification.types";

export const notificationTemplates: NotificationTemplate[] = [
  {
    id: "tpl-booking-confirmed",
    title: "Booking Confirmed",
    category: "booking",
    channels: ["email", "sms", "whatsapp", "push"],
    subject: "Your Nexivo booking is confirmed",
    body: "Hello {{customerName}}, your {{serviceType}} booking {{bookingReference}} is confirmed.",
    variables: ["customerName", "serviceType", "bookingReference"],
    enabled: true
  },
  {
    id: "tpl-payment-received",
    title: "Payment Received",
    category: "payment",
    channels: ["email", "push"],
    subject: "Payment received by Nexivo",
    body: "We received {{amount}} for booking {{bookingReference}}.",
    variables: ["amount", "bookingReference"],
    enabled: true
  },
  {
    id: "tpl-checkin-reminder",
    title: "Stay Check-in Reminder",
    category: "reminder",
    channels: ["email", "whatsapp", "push"],
    subject: "Your stay starts soon",
    body: "Reminder: your stay at {{propertyName}} starts on {{checkInDate}}.",
    variables: ["propertyName", "checkInDate"],
    enabled: true
  },
  {
    id: "tpl-car-pickup-reminder",
    title: "Car Pickup Reminder",
    category: "reminder",
    channels: ["sms", "whatsapp", "push"],
    subject: "Car pickup reminder",
    body: "Your {{vehicleName}} pickup is scheduled at {{pickupLocation}} on {{pickupDate}}.",
    variables: ["vehicleName", "pickupLocation", "pickupDate"],
    enabled: true
  },
  {
    id: "tpl-laundry-pickup",
    title: "Laundry Pickup Scheduled",
    category: "booking",
    channels: ["whatsapp", "push", "email"],
    subject: "Laundry pickup scheduled",
    body: "Your Laundrex pickup is scheduled for {{pickupDate}} at {{pickupAddress}}.",
    variables: ["pickupDate", "pickupAddress"],
    enabled: true
  },
  {
    id: "tpl-security-login",
    title: "Security Login Alert",
    category: "security",
    channels: ["email", "push"],
    subject: "New login to your Nexivo account",
    body: "A new login was detected on your Nexivo account from {{location}}.",
    variables: ["location"],
    enabled: true
  },
  {
    id: "tpl-business-lead",
    title: "New Business Demo Request",
    category: "business",
    channels: ["email", "push"],
    subject: "New DSS demo request",
    body: "{{businessName}} requested a demo for {{productInterest}}.",
    variables: ["businessName", "productInterest"],
    enabled: true
  }
];

export const defaultNotificationPreferences: NotificationPreference[] = [
  {
    channel: "email",
    enabled: true,
    bookingUpdates: true,
    paymentUpdates: true,
    reminders: true,
    promotions: true,
    securityAlerts: true,
    businessUpdates: true
  },
  {
    channel: "sms",
    enabled: true,
    bookingUpdates: true,
    paymentUpdates: false,
    reminders: true,
    promotions: false,
    securityAlerts: true,
    businessUpdates: false
  },
  {
    channel: "whatsapp",
    enabled: true,
    bookingUpdates: true,
    paymentUpdates: false,
    reminders: true,
    promotions: true,
    securityAlerts: false,
    businessUpdates: false
  },
  {
    channel: "push",
    enabled: true,
    bookingUpdates: true,
    paymentUpdates: true,
    reminders: true,
    promotions: true,
    securityAlerts: true,
    businessUpdates: true
  }
];

export const notificationLogs: NotificationLog[] = [];
