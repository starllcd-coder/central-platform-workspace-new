from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_usertwofactor"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserTwoFactorBackupCode",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code_hash", models.CharField(max_length=128, unique=True)),
                ("is_used", models.BooleanField(default=False)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("two_factor", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="backup_codes", to="accounts.usertwofactor")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.AddIndex(
            model_name="usertwofactorbackupcode",
            index=models.Index(fields=["two_factor", "is_used"], name="accounts_us_two_fac_13fb04_idx"),
        ),
    ]
