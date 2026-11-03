from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0012_alter_tenantdatabaseconfiguration_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="account_type",
            field=models.CharField(
                choices=[("production", "Production"), ("demo", "Demo")],
                default="production",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="tenant",
            name="demo_converted_to_paid_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tenant",
            name="demo_expires_on",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="tenant",
            name="demo_notes",
            field=models.TextField(blank=True, default=""),
        ),
    ]
