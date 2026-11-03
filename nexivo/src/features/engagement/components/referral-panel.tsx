import { Gift, Share2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { referralRewards } from "@/features/engagement/data/engagement-data";

export function ReferralPanel() {
  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="grid gap-6 md:grid-cols-2">
          {referralRewards.map((referral) => (
            <article
              key={referral.id}
              className="rounded-4xl border border-slate-200 bg-white p-6 shadow-premium"
            >
              <div className="flex items-start justify-between gap-5">
                <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-luxury-gold/15 text-luxury-bronze">
                  {referral.type === "customer" ? <Gift size={24} /> : <Share2 size={24} />}
                </div>

                <Badge variant={referral.status === "active" ? "success" : "secondary"}>
                  {referral.status}
                </Badge>
              </div>

              <h3 className="mt-6 font-heading text-2xl font-semibold text-luxury-ink">
                {referral.title}
              </h3>

              <p className="mt-3 text-sm leading-7 text-slate-600">{referral.description}</p>

              <p className="mt-5 rounded-3xl bg-luxury-mist px-4 py-3 text-sm font-semibold text-slate-700">
                Reward: {referral.reward}
              </p>

              <Button variant="luxury" className="mt-6" disabled={referral.status !== "active"}>
                Generate Referral Link
              </Button>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
