import { CustomerRewardsPanel } from "@/features/customer/components/customer-rewards-panel";
import { rewardActivities } from "@/features/customer/data/customer-dashboard-data";

export default function CustomerRewardsPage() {
  return <CustomerRewardsPanel activities={rewardActivities} />;
}
