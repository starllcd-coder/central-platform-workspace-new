const items = [

  "Mobile navigation",

  "Tablet layout",

  "Desktop layout",

  "Property cards",

  "Vehicle cards",

  "Laundry cards",

  "Customer dashboard",

  "Partner dashboard",

  "Admin dashboard",

  "Business pages"

];

export function ResponsiveAuditPanel() {
  return (
    <section className="section-padding bg-white">

      <div className="nexivo-container">

        <div className="rounded-4xl border border-slate-200 bg-white p-6 shadow-premium">

          <h2 className="font-heading text-3xl font-semibold text-luxury-ink">
            Responsive Audit Checklist
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