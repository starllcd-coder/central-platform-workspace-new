import { CustomerNotificationsList } from "@/features/customer/components/customer-notifications-list";
import { customerNotifications } from "@/features/customer/data/customer-dashboard-data";

export default function CustomerNotificationsPage() {
  return <CustomerNotificationsList notifications={customerNotifications} />;
}
