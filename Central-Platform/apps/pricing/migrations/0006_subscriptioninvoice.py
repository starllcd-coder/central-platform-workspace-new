from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("pricing", "0005_addon_tenantaddonsubscription_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="SubscriptionInvoice",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("invoice_code", models.CharField(max_length=50, unique=True)),
                ("amount_due", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("currency", models.CharField(default="OMR", max_length=10)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("due_date", models.DateField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("paid", "Paid"),
                            ("overdue", "Overdue"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "plan_version",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscription_invoices", to="pricing.planversion"),
                ),
                (
                    "subscription",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="invoices", to="pricing.tenantsubscription"),
                ),
                (
                    "tenant",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subscription_invoices", to="tenants.tenant"),
                ),
            ],
            options={
                "ordering": ["-created_at", "-id"],
                "unique_together": {("subscription", "period_start", "period_end")},
            },
        ),
        migrations.AddIndex(
            model_name="subscriptioninvoice",
            index=models.Index(fields=["status", "due_date"], name="pricing_sub_status_08123d_idx"),
        ),
        migrations.AddIndex(
            model_name="subscriptioninvoice",
            index=models.Index(fields=["tenant", "status"], name="pricing_sub_tenant__dd30bd_idx"),
        ),
    ]
