import { Gift, Star } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { RewardActivity } from "@/features/customer/types/customer.types";

type CustomerRewardsPanelProps = {
  activities: RewardActivity[];
};

export function CustomerRewardsPanel({ activities }: CustomerRewardsPanelProps) {
  const totalPoints = activities.reduce((sum, activity) => sum + activity.points, 0);

  return (
    <Card variant="premium">
      <CardHeader>
        <CardTitle>Nexivo Rewards</CardTitle>
        <p className="text-sm text-slate-600">
          Rewards from stays, car rentals, laundry orders, referrals, and future promotions.
        </p>
      </CardHeader>

      <CardContent>
        <div className="rounded-4xl bg-midnight-gradient p-6 text-white shadow-premium">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-white/10 text-luxury-gold">
              <Star size={25} />
            </div>
            <div>
              <p className="text-sm text-white/65">Available points</p>
              <div className="font-heading text-4xl font-semibold">{totalPoints}</div>
            </div>
          </div>
        </div>

        <div className="mt-5 space-y-3">
          {activities.map((activity) => (
            <div
              key={activity.id}
              className="flex items-center justify-between rounded-3xl border border-slate-200 bg-white p-4 shadow-soft"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-luxury-gold/15 text-luxury-bronze">
                  <Gift size={18} />
                </div>
                <div>
                  <p className="font-semibold text-luxury-ink">{activity.label}</p>
                  <p className="text-sm text-slate-500">{activity.date}</p>
                </div>
              </div>

              <span className="font-heading text-lg font-semibold text-emerald-700">
                +{activity.points}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
