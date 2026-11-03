import json
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.catalog.models import ItemServicePrice
from .central_connector import verify_central_request

def resolve_price(resource):
    if str(resource).startswith("price-"):
        pk=str(resource)[6:]
        return ItemServicePrice.objects.select_related("item","service").filter(pk=int(pk),item__is_active=True,service__is_active=True).first() if pk.isdigit() else None
    prices=ItemServicePrice.objects.select_related("item","service").filter(service__is_active=True,item__is_active=True)
    prices=prices.filter(service_id=int(resource)) if str(resource).isdigit() else prices.filter(service__code=resource)
    return prices.first() if prices.count()==1 else None

def effective_unit_price(price):
    from apps.catalog.models import BranchItemServicePrice
    branch=getattr(settings,"CENTRAL_BRANCH_CODE","muscat")
    override=BranchItemServicePrice.objects.filter(branch__code=branch,item=price.item,service=price.service).first()
    return override.price if override else price.price

def quote(payload):
    price=resolve_price(str(payload.get("provider_resource_id") or ""))
    if not price: raise ValueError("Select an available laundry item and service.")
    if not parse_date(str(payload.get("pickupDate") or payload.get("pickup_date") or "")): raise ValueError("A pickup date is required.")
    quantity=int(payload.get("quantity") or 1)
    if quantity<1 or quantity>10000: raise ValueError("Invalid quantity.")
    unit_price=effective_unit_price(price)
    total=unit_price*quantity
    if total<=0: raise ValueError("Laundry rate is not configured.")
    return {"amount":str(total.quantize(Decimal("0.001"))),"currency":getattr(settings,"CENTRAL_CURRENCY","OMR"),
        "quantity":quantity,"unit_price":str(unit_price),"tax":"0.000","policy":{}}

@csrf_exempt
@require_POST
def quote_view(request):
    valid,error=verify_central_request(request)
    if not valid:return JsonResponse({"ok":False,"error":error},status=403)
    try:return JsonResponse({"ok":True,**quote(json.loads(request.body))})
    except (ValueError,TypeError,AttributeError) as exc:return JsonResponse({"ok":False,"error":str(exc)},status=422)
