from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("connectors", "0002_connectorevent_external_event_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConnectorRequestNonce",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nonce", models.CharField(max_length=120, unique=True)),
                ("event_type", models.CharField(default="", max_length=30)),
                ("source_timestamp", models.DateTimeField(blank=True, null=True)),
                ("request_signature", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("module", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="connector_nonces", to="tenants.module")),
                ("tenant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="connector_nonces", to="tenants.tenant")),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="connectorrequestnonce",
            index=models.Index(fields=["event_type", "created_at"], name="connectors__event_t_337f7a_idx"),
        ),
        migrations.AddIndex(
            model_name="connectorrequestnonce",
            index=models.Index(fields=["module", "created_at"], name="connectors__module__8f205f_idx"),
        ),
        migrations.AddIndex(
            model_name="connectorrequestnonce",
            index=models.Index(fields=["tenant", "created_at"], name="connectors__tenant__2f9165_idx"),
        ),
    ]
