from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0013_tenant_demo_fields"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DemoTenantRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("business_name", models.CharField(max_length=180)),
                ("requested_tenant_code", models.CharField(blank=True, default="", max_length=40)),
                ("owner_name", models.CharField(blank=True, max_length=180)),
                ("owner_email", models.EmailField(blank=True, max_length=254)),
                ("owner_phone", models.CharField(blank=True, max_length=50)),
                ("country", models.CharField(blank=True, max_length=80)),
                ("currency", models.CharField(default="OMR", max_length=10)),
                ("timezone", models.CharField(default="Asia/Dubai", max_length=60)),
                ("module_type", models.CharField(choices=[("staylux", "StayLux"), ("drivesphere", "DriveSphere"), ("laundrex", "Laundrex")], max_length=20)),
                ("requested_duration_days", models.PositiveSmallIntegerField(default=14)),
                ("request_notes", models.TextField(blank=True, default="")),
                ("status", models.CharField(choices=[("requested", "Requested"), ("approved", "Approved"), ("rejected", "Rejected"), ("cancelled", "Cancelled")], default="requested", max_length=20)),
                ("review_notes", models.TextField(blank=True, default="")),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("approved_tenant", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="source_demo_requests", to="tenants.tenant")),
                ("requested_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="demo_tenant_requests", to=settings.AUTH_USER_MODEL)),
                ("reviewed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_demo_tenant_requests", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["status", "-created_at"]},
        ),
    ]
