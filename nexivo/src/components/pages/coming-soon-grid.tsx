import { Card, CardContent } from "@/components/ui/card";

type ComingSoonGridProps = {
  items: string[];
};

export function ComingSoonGrid({ items }: ComingSoonGridProps) {
  return (
    <section className="section-padding bg-white">
      <div className="nexivo-container">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <Card key={item} variant="premium">
              <CardContent className="p-6">
                <h3 className="font-heading text-lg font-semibold text-luxury-ink">{item}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">
                  This section is prepared in the Nexivo route architecture and will be expanded in upcoming development chunks.
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
