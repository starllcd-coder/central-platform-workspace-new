import { Briefcase, Calendar, Landmark, Plane, ShoppingBag, TreePalm, UsersRound } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import type { DestinationExperience } from "@/features/destinations/types/destination.types";

type DestinationExperiencesSectionProps = {
  experiences: DestinationExperience[];
};

const iconMap = {
  nature: TreePalm,
  shopping: ShoppingBag,
  business: Briefcase,
  culture: Landmark,
  family: UsersRound,
  airport: Plane,
  seasonal: Calendar
};

export function DestinationExperiencesSection({
  experiences
}: DestinationExperiencesSectionProps) {
  if (experiences.length === 0) return null;

  return (
    <section className="section-padding bg-luxury-mist">
      <div className="nexivo-container">
        <div className="mb-8">
          <p className="eyebrow mb-5">Experiences</p>
          <h2 className="font-heading text-3xl font-semibold text-luxury-ink md:text-5xl">
            Destination experience ideas.
          </h2>
        </div>

        <div className="grid gap-5 md:grid-cols-3">
          {experiences.map((experience) => {
            const Icon = iconMap[experience.category];

            return (
              <article
                key={experience.id}
                className="rounded-4xl border border-slate-200 bg-white p-6 shadow-soft"
              >
                <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-50 text-brand-700">
                  <Icon size={21} />
                </div>

                <Badge variant="outline" className="mt-5">
                  {experience.category}
                </Badge>

                <h3 className="mt-4 font-heading text-xl font-semibold text-luxury-ink">
                  {experience.title}
                </h3>

                <p className="mt-3 text-sm leading-7 text-slate-600">
                  {experience.description}
                </p>
              </article>
            );
          })}
        </div>
      </div>
    </section>
  );
}
