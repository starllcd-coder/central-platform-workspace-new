from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("connectors", "0004_connectorhealthlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="connectorevent",
            name="auth_key_version",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="connectorhealthlog",
            name="auth_key_version",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
    ]
