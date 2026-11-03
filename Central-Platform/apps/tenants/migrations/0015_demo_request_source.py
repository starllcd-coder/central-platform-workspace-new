from django.db import migrations, models


def populate_product_interest(apps, schema_editor):
    DemoTenantRequest = apps.get_model("tenants", "DemoTenantRequest")
    for row in DemoTenantRequest.objects.filter(product_interest="").iterator():
        row.product_interest = row.module_type
        row.save(update_fields=["product_interest"])


class Migration(migrations.Migration):
    dependencies = [("tenants", "0014_demotenantrequest")]

    operations = [
        migrations.AddField(
            model_name="demotenantrequest",
            name="source",
            field=models.CharField(
                choices=[("central", "Central Platform"), ("nexivo", "Nexivo Website")],
                default="central",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="demotenantrequest",
            name="external_reference",
            field=models.CharField(blank=True, default="", max_length=120),
        ),
        migrations.AddField(
            model_name="demotenantrequest",
            name="product_interest",
            field=models.CharField(
                blank=True,
                choices=[
                    ("staylux", "StayLux"),
                    ("drivesphere", "DriveSphere"),
                    ("laundrex", "Laundrex"),
                    ("central-platform", "Central Platform"),
                    ("multiple", "Multiple DSS Products"),
                ],
                default="",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="demotenantrequest",
            name="module_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("staylux", "StayLux"),
                    ("drivesphere", "DriveSphere"),
                    ("laundrex", "Laundrex"),
                ],
                default="",
                max_length=20,
            ),
        ),
        migrations.RunPython(populate_product_interest, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="demotenantrequest",
            constraint=models.UniqueConstraint(
                condition=models.Q(("external_reference", ""), _negated=True),
                fields=("source", "external_reference"),
                name="unique_demo_request_source_reference",
            ),
        ),
    ]
