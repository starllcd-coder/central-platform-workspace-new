from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("tenants", "0008_tenantbranding_domain_failure_reason_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="GatewayConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[("thawani", "Thawani"), ("tap", "Tap Payments"), ("stripe", "Stripe")], max_length=20, unique=True)),
                ("is_enabled", models.BooleanField(default=True)),
                ("priority", models.PositiveIntegerField(default=100)),
                ("api_base_url", models.CharField(blank=True, default="", max_length=255)),
                ("public_key", models.CharField(blank=True, default="", max_length=255)),
                ("secret_key", models.CharField(blank=True, default="", max_length=255)),
                ("webhook_secret", models.CharField(blank=True, default="", max_length=255)),
                ("supports_partial_refund", models.BooleanField(default=True)),
                ("supports_card_guarantee", models.BooleanField(default=True)),
                ("settings_json", models.JSONField(blank=True, default=dict)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["priority", "provider"]},
        ),
        migrations.CreateModel(
            name="PaymentWebhookLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider", models.CharField(choices=[("thawani", "Thawani"), ("tap", "Tap Payments"), ("stripe", "Stripe")], max_length=20)),
                ("event_id", models.CharField(blank=True, db_index=True, default="", max_length=120)),
                ("signature_valid", models.BooleanField(default=False)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("processing_status", models.CharField(default="received", max_length=30)),
                ("detail", models.CharField(blank=True, default="", max_length=255)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-received_at", "-id"]},
        ),
        migrations.CreateModel(
            name="RoutingRule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("is_enabled", models.BooleanField(default=True)),
                ("priority", models.PositiveIntegerField(default=100)),
                ("gateway", models.CharField(choices=[("thawani", "Thawani"), ("tap", "Tap Payments"), ("stripe", "Stripe")], max_length=20)),
                ("countries_csv", models.CharField(blank=True, default="", max_length=255)),
                ("currencies_csv", models.CharField(blank=True, default="", max_length=255)),
                ("module_codes_csv", models.CharField(blank=True, default="", max_length=255)),
                ("payment_methods_csv", models.CharField(blank=True, default="", max_length=255)),
                ("notes", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["priority", "id"]},
        ),
        migrations.CreateModel(
            name="CentralPayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("payment_id", models.CharField(max_length=64, unique=True)),
                ("external_reference", models.CharField(blank=True, db_index=True, default="", max_length=120)),
                ("idempotency_key", models.CharField(blank=True, db_index=True, default="", max_length=120)),
                ("booking_id", models.CharField(blank=True, default="", max_length=80)),
                ("parent_booking_id", models.CharField(blank=True, default="", max_length=80)),
                ("customer_id", models.CharField(blank=True, default="", max_length=80)),
                ("business_id", models.CharField(blank=True, default="", max_length=80)),
                ("gateway_name", models.CharField(choices=[("thawani", "Thawani"), ("tap", "Tap Payments"), ("stripe", "Stripe")], max_length=20)),
                ("payment_method", models.CharField(default="card", max_length=40)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("currency", models.CharField(default="OMR", max_length=10)),
                ("country_code", models.CharField(blank=True, default="", max_length=2)),
                ("transaction_status", models.CharField(choices=[("created", "Created"), ("pending", "Pending"), ("authorized", "Authorized"), ("captured", "Captured"), ("failed", "Failed"), ("cancelled", "Cancelled"), ("refunded", "Refunded"), ("partially_refunded", "Partially Refunded"), ("expired", "Expired")], default="created", max_length=30)),
                ("refund_status", models.CharField(default="none", max_length=30)),
                ("commission_amount", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("business_share", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("is_card_guarantee", models.BooleanField(default=False)),
                ("is_extension_payment", models.BooleanField(default=False)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("last_error", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("module", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="central_payments", to="tenants.module")),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="central_payments", to="tenants.tenant")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="CentralRefund",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("refund_id", models.CharField(max_length=64, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("is_partial", models.BooleanField(default=False)),
                ("reason", models.CharField(blank=True, default="", max_length=255)),
                ("status", models.CharField(default="processed", max_length=30)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("payment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="refunds", to="paymentsvc.centralpayment")),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.AddIndex(
            model_name="centralpayment",
            index=models.Index(fields=["tenant", "module", "transaction_status"], name="paymentsvc_c_tenant__8fe230_idx"),
        ),
        migrations.AddIndex(
            model_name="centralpayment",
            index=models.Index(fields=["booking_id"], name="paymentsvc_c_booking_af5570_idx"),
        ),
        migrations.AddIndex(
            model_name="centralpayment",
            index=models.Index(fields=["external_reference"], name="paymentsvc_c_externa_8f860c_idx"),
        ),
    ]

