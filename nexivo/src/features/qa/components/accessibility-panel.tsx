const items = [

  "Keyboard navigation",

  "Focus visibility",

  "Semantic headings",

  "ARIA labels",

  "Screen reader support",

  "Form accessibility",

  "Color contrast"

];

export function AccessibilityPanel() {
  return (
    <section className="section-padding bg-luxury-mist">

      <div className="nexivo-container">

        <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">

          <h2 className="font-heading text-3xl font-semibold text-luxury-ink">
            Accessibility Readiness
          </h2>

          <div className="mt-6 grid gap-3 md:grid-cols-2">

            {items.map((item) => (

              <div
                key={item}
                className="rounded-3xl border border-slate-200 bg-luxury-mist px-4 py-3"
              >
                {item}
              </div>

            ))}

          </div>

        </div>

      </div>

    </section>
  );
}