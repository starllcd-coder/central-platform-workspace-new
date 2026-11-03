from django.utils import timezone
from apps.settings_app.models import BusinessProfile

def snapshots(instance, deleted=False):
    yield {"resource_id": str(instance.pk), "name": f"{instance.brand.name} {instance.model.name} ({instance.plate_number})",
        "base_price": str(instance.daily_rate), "currency": BusinessProfile.get_solo().currency_code or "OMR",
        "active": not deleted and instance.status not in {"MAINTENANCE", "INACTIVE"}, "unit": "day",
        "updated_at": timezone.now().isoformat(), "seats": instance.seats, "transmission": instance.transmission.lower(),
        "fuelType": instance.fuel.lower(), "deposit": str(instance.deposit)}

def related_resources(instance):
    from apps.fleet.models import Vehicle
    label = instance._meta.label_lower
    if label == "fleet.vehiclebrand": return Vehicle.objects.filter(brand=instance)
    if label == "fleet.vehiclemodel": return Vehicle.objects.filter(model=instance)
    return Vehicle.objects.all()
