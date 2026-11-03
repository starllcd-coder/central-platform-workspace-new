from django.conf import settings
from django.utils import timezone

def snapshots(instance, deleted=False):
    from apps.orders.central_quotes import effective_unit_price
    yield {"resource_id": f"price-{instance.pk}", "name": f"{instance.item.name} - {instance.service.name}",
        "base_price": str(effective_unit_price(instance)), "currency": getattr(settings, "CENTRAL_CURRENCY", "OMR"),
        "active": not deleted and instance.item.is_active and instance.service.is_active, "unit": "piece",
        "updated_at": timezone.now().isoformat(), "service_id": instance.service_id, "item_id": instance.item_id}

def related_resources(instance):
    from apps.catalog.models import ItemServicePrice
    if instance._meta.model_name == "branchitemserviceprice":
        return ItemServicePrice.objects.filter(item=instance.item,service=instance.service)
    return ItemServicePrice.objects.filter(**({"service": instance} if instance._meta.model_name == "service" else {"item": instance}))
