from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from apps.tenants.models import MarketplaceListing, TenantModule

EVENT_NAME = "marketplace.resource.updated"

def apply_inventory(payload, tenant, module):
    if payload.get("event_name") != EVENT_NAME:
        return
    if not tenant or not module or not TenantModule.objects.filter(tenant=tenant, module=module, enabled=True).exists():
        raise ValueError("An enabled tenant/module binding is required.")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("Resource data is required.")
    resource = str(data.get("resource_id") or "").strip()
    if not resource or len(resource) > 120:
        raise ValueError("A valid provider resource ID is required.")
    try:
        updated = parse_datetime(str(data.get("updated_at") or ""))
        price = Decimal(str(data.get("base_price", "0")))
        if not price.is_finite() or price < 0 or price >= Decimal("1000000000"):
            raise ValueError("Invalid price")
    except (ValueError, TypeError, InvalidOperation):
        raise ValueError("Invalid resource timestamp or price.")
    if not updated or timezone.is_naive(updated) or updated > timezone.now() + timedelta(minutes=5):
        raise ValueError("A timezone-aware resource timestamp is required.")
    if str(data.get("currency") or "").upper() != tenant.currency.upper():
        raise ValueError("Resource currency does not match the tenant currency.")
    listing, _ = MarketplaceListing.objects.get_or_create(tenant=tenant, module=module, provider_resource_id=resource,
        defaults={"is_active": False})
    listing = MarketplaceListing.objects.select_for_update().get(pk=listing.pk)
    if listing.provider_updated_at and updated <= listing.provider_updated_at:
        return
    listing.provider_updated_at = updated
    listing.provider_resource_name = str(data.get("name") or resource)[:180]
    listing.provider_resource_unit = str(data.get("unit") or "")[:40]
    listing.base_price = price
    listing.is_active = data.get("active") is True and price > 0
    listing.snapshot = data
    listing.save()
