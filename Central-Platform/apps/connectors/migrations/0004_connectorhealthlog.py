from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("connectors", "0003_connectorrequestnonce"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConnectorHealthLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("endpoint", models.CharField(max_length=120)),
                ("status_code", models.IntegerField(default=200)),
                ("is_success", models.BooleanField(default=True)),
                ("reason", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("module", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="connector_health_logs", to="tenants.module")),
                ("tenant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="connector_health_logs", to="tenants.tenant")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="connectorhealthlog",
            index=models.Index(fields=["endpoint", "created_at"], name="connectors__endpoint_0442fe_idx"),
        ),
        migrations.AddIndex(
            model_name="connectorhealthlog",
            index=models.Index(fields=["is_success", "created_at"], name="connectors__is_succ_24c0a7_idx"),
        ),
    ]
