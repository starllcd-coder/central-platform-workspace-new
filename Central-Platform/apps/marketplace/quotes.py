import hashlib
import json
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.core import signing
from django.http import JsonResponse
from django.db.models import Exists,OuterRef
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.tenants.models import MarketplaceListing, TenantModule
from apps.connectors.client import provider_request, ProviderUnavailable

SALT="marketplace-quote-v1"
KEYS=("checkIn","checkOut","check_in","check_out","pickupDate","returnDate","pickup_date","return_date","quantity","guests")

def selection(payload):
    return hashlib.sha256(json.dumps({key:str(payload[key]) for key in KEYS if key in payload},sort_keys=True).encode()).hexdigest()

def public_listings():
    bindings=TenantModule.objects.filter(tenant_id=OuterRef("tenant_id"),module_id=OuterRef("module_id"),enabled=True,marketplace_enabled=True)
    return MarketplaceListing.objects.select_related("tenant","module").annotate(published_binding=Exists(bindings)).filter(published_binding=True,is_active=True,tenant__status__in=["active","trial"])

def terms(result):
    return hashlib.sha256(json.dumps({key:result.get(key) for key in ["amount","currency","policy","tax","quantity","unit_price"]},sort_keys=True).encode()).hexdigest()

def get_listing(slug):
    listing=public_listings().filter(public_slug=slug).first()
    if not listing or listing.tenant.status not in {"active","trial"} or not TenantModule.objects.filter(
        tenant=listing.tenant,module=listing.module,enabled=True,marketplace_enabled=True).exists():
        raise ValueError("Listing is unavailable.")
    return listing

def calculate(listing,payload):
    if getattr(settings,"MARKETPLACE_REQUIRE_QUOTES",False) or listing.snapshot:
        result=provider_request(listing.tenant,listing.module,"quote",{**payload,"provider_resource_id":listing.provider_resource_id})
        amount=Decimal(str(result["amount"]))
        currency=str(result["currency"])
    else:
        from django.utils.dateparse import parse_date
        if listing.module.code in {"staylux","drivesphere"}:
            start=parse_date(str(payload.get("checkIn") or payload.get("check_in") or payload.get("pickupDate") or payload.get("pickup_date") or ""))
            end=parse_date(str(payload.get("checkOut") or payload.get("check_out") or payload.get("returnDate") or payload.get("return_date") or ""))
            if not start or not end or end<=start or (end-start).days>366: raise ValueError("Valid booking dates are required.")
            count=(end-start).days
        else:
            count=int(payload.get("quantity") or 1)
            if count<1 or count>10000: raise ValueError("Invalid quantity.")
        amount=listing.base_price*count;currency=listing.tenant.currency
        result={"policy":{},"tax":"0.000","quantity":count}
    if not amount.is_finite() or amount<=0 or currency!=listing.tenant.currency:
        raise ValueError("The provider quote has an invalid amount or currency.")
    return {**result,"amount":str(amount.quantize(Decimal("0.001"))),"currency":currency}

@csrf_exempt
@require_POST
def quote_api(request):
    try:
        payload=json.loads(request.body)
        listing=get_listing(str(payload.get("listingSlug") or ""))
        result=calculate(listing,payload)
        result["quoteToken"]=signing.dumps({"listing":listing.pk,"selection":selection(payload),"amount":result["amount"],"currency":result["currency"],"terms":terms(result)},salt=SALT)
        result["expiresIn"]=600
        return JsonResponse(result)
    except ProviderUnavailable as exc: return JsonResponse({"detail":str(exc)},status=503)
    except (ValueError,TypeError,KeyError,InvalidOperation,AttributeError) as exc: return JsonResponse({"detail":str(exc)},status=422)

def verify_quote(listing,payload,amount,current=None):
    token=payload.get("quoteToken")
    if not token:
        if getattr(settings,"MARKETPLACE_REQUIRE_QUOTES",False): raise ValueError("Review a current quote before confirming this booking.")
        return
    try: data=signing.loads(token,salt=SALT,max_age=600)
    except signing.BadSignature as exc: raise ValueError("Quote expired. Review a new quote.") from exc
    if current is not None and data.get("terms") != terms(current): raise ValueError("Quote terms changed. Review a new quote.")
    if data.get("currency")!=listing.tenant.currency or data.get("listing")!=listing.pk or data.get("selection")!=selection(payload) or Decimal(data["amount"])!=amount:
        raise ValueError("Booking details or price changed. Review a new quote.")
