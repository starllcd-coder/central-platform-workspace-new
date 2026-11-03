from django.conf import settings
from django.utils import timezone

def snapshots(instance, deleted=False):
    if str(instance.property_profile_id) != str(getattr(settings, "CENTRAL_PROPERTY_ID", "")):
        return
    yield {"resource_id": str(instance.pk), "name": f"{instance.property_profile.name_en} - {instance.code}",
        "base_price": str(instance.daily_price or instance.unit_type.base_rate), "currency": instance.property_profile.currency,
        "active": not deleted and instance.is_active and instance.status != "maintenance", "unit": "night",
        "updated_at": timezone.now().isoformat(), "capacity": instance.guest_capacity,
        "city": instance.property_profile.city, "country": instance.property_profile.country}

def related_resources(instance):
    from inventory.models import Unit
    label = instance._meta.label_lower
    if label == "inventory.unittype": return Unit.objects.filter(unit_type=instance)
    if label == "settings_app.propertyprofile": return Unit.objects.filter(property_profile=instance)
    return Unit.objects.filter(property_profile_id=instance.property_profile_id)
