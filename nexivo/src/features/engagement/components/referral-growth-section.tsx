import { Gift, Share2, UsersRound } from "lucide-react";

const steps = [
  {
    title: "Share Nexivo",
    description: "Customer or business receives a unique referral link.",
    icon: Share2
  },
  {
    title: "Referral completes action",
    description: "Reward triggers only after completed booking or successful business onboarding.",
    icon: UsersRound
  },
  {
    title: "Reward released",
    description: "Customer gets points or business receives promotional credit.",
    icon: Gift
  }
];

export function ReferralGrowthSection() {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="mb-10 text-center">
          <p className="eyebrow mb-5 justify-center">Referral Logic</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Referral rewards should be controlled and verified.
          </h2>
        </div>

        <div className="grid gap-5 md:grid-cols-3">
          {steps.map((step) => {
            const Icon = step.icon;

            return (
              <article key={step.title} className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft">
                <Icon size={25} className="text-brand-700" />
                <h3 className="mt-5 font-heading text-2xl font-semibold text-luxury-ink">
                  {step.title}
                </h3>
                <p className="mt-3 text-sm leading-7 text-slate-600">{step.description}</p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}