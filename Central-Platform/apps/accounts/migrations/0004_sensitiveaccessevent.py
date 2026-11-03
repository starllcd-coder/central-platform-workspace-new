from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_usertwofactorbackupcode"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SensitiveAccessEvent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("permission_code", models.CharField(max_length=120)),
                ("path", models.CharField(max_length=255)),
                ("ip_address", models.CharField(blank=True, default="", max_length=64)),
                ("user_agent", models.CharField(blank=True, default="", max_length=255)),
                (
                    "status",
                    models.CharField(
                        choices=[("granted", "Granted"), ("denied", "Denied"), ("challenge", "Challenge Required")],
                        default="granted",
                        max_length=20,
                    ),
                ),
                ("reason", models.CharField(blank=True, default="", max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="sensitive_access_events", to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="sensitiveaccessevent",
            index=models.Index(fields=["user", "created_at"], name="accounts_se_user_id_edb707_idx"),
        ),
        migrations.AddIndex(
            model_name="sensitiveaccessevent",
            index=models.Index(fields=["permission_code", "created_at"], name="accounts_se_permiss_3f22a8_idx"),
        ),
        migrations.AddIndex(
            model_name="sensitiveaccessevent",
            index=models.Index(fields=["status", "created_at"], name="accounts_se_status_6d2308_idx"),
        ),
    ]
