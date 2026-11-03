from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Delivery", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name="ID")),
            ("external_id", models.CharField(max_length=80, unique=True)),
            ("payload_hash", models.CharField(max_length=64)),
            ("booking_id", models.PositiveBigIntegerField(null=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name="RequestNonce", fields=[
            ("id", models.BigAutoField(primary_key=True, serialize=False, auto_created=True, verbose_name="ID")),
            ("nonce", models.CharField(max_length=128, unique=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ]),
    ]
