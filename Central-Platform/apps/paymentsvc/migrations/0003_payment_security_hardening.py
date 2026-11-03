from django.db import migrations, models
import django.db.models.deletion


def encrypt_gateway_secrets(apps, schema_editor):
    from apps.tenants.database_crypto import encrypt_database_secret

    GatewayConfig = apps.get_model("paymentsvc", "GatewayConfig")
    for row in GatewayConfig.objects.all().iterator():
        row.secret_key_encrypted = encrypt_database_secret(row.secret_key)
        row.webhook_secret_encrypted = encrypt_database_secret(row.webhook_secret)
        row.save(update_fields=["secret_key_encrypted", "webhook_secret_encrypted"])


def deduplicate_security_keys(apps, schema_editor):
    CentralPayment = apps.get_model("paymentsvc", "CentralPayment")
    PaymentWebhookLog = apps.get_model("paymentsvc", "PaymentWebhookLog")

    seen_payment_keys = set()
    for row in CentralPayment.objects.exclude(idempotency_key="").order_by("id").iterator():
        key = (row.tenant_id, row.idempotency_key)
        if key in seen_payment_keys:
            row.idempotency_key = ""
            row.save(update_fields=["idempotency_key"])
        else:
            seen_payment_keys.add(key)

    seen_events = set()
    for row in PaymentWebhookLog.objects.exclude(event_id="").order_by("id").iterator():
        key = (row.provider, row.event_id)
        if key in seen_events:
            row.event_id = f"legacy-duplicate-{row.id}"
            row.save(update_fields=["event_id"])
        else:
            seen_events.add(key)


class Migration(migrations.Migration):
    dependencies = [("paymentsvc", "0002_rename_paymentsvc_c_tenant__8fe230_idx_paymentsvc__tenant__7c4e92_idx_and_more")]

    operations = [
        migrations.AddField(
            model_name="gatewayconfig",
            name="secret_key_encrypted",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="gatewayconfig",
            name="webhook_secret_encrypted",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.RunPython(encrypt_gateway_secrets, migrations.RunPython.noop),
        migrations.RemoveField(model_name="gatewayconfig", name="secret_key"),
        migrations.RemoveField(model_name="gatewayconfig", name="webhook_secret"),
        migrations.CreateModel(
            name="PaymentRequestNonce",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nonce", models.CharField(max_length=120, unique=True)),
                ("method", models.CharField(max_length=10)),
                ("path", models.CharField(max_length=255)),
                ("source_timestamp", models.DateTimeField()),
                ("request_signature", models.CharField(max_length=128)),
                ("auth_key_version", models.CharField(blank=True, default="", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="paymentrequestnonce",
            index=models.Index(fields=["created_at"], name="paymentsvc__created_5f4e7e_idx"),
        ),
        migrations.RunPython(deduplicate_security_keys, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="centralpayment",
            constraint=models.CheckConstraint(condition=models.Q(("amount__gt", 0)), name="payment_amount_positive"),
        ),
        migrations.AddConstraint(
            model_name="centralpayment",
            constraint=models.UniqueConstraint(
                condition=models.Q(("idempotency_key", ""), _negated=True),
                fields=("tenant", "idempotency_key"),
                name="unique_tenant_payment_idempotency",
            ),
        ),
        migrations.AddConstraint(
            model_name="centralrefund",
            constraint=models.CheckConstraint(condition=models.Q(("amount__gt", 0)), name="refund_amount_positive"),
        ),
        migrations.AddConstraint(
            model_name="paymentwebhooklog",
            constraint=models.UniqueConstraint(
                condition=models.Q(("event_id", ""), _negated=True),
                fields=("provider", "event_id"),
                name="unique_provider_webhook_event",
            ),
        ),
    ]
