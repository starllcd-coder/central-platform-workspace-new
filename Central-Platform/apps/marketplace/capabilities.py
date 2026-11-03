from datetime import timedelta
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from apps.connectors.models import ConnectorEvent,ConnectorHealthLog,ConnectorRequestNonce
from apps.paymentsvc.models import CentralPayment

@require_GET
def capabilities(request):
    window=timezone.now()-timedelta(minutes=15)
    resources=ConnectorEvent.objects.filter(payload__event_name="marketplace.resource.updated",received_at__gte=window).exists()
    pricing=ConnectorHealthLog.objects.filter(endpoint="provider.quote",is_success=True,created_at__gte=window).exists()
    sso=ConnectorRequestNonce.objects.filter(event_type="sso.consume",created_at__gte=window).exists()
    live=getattr(settings,"PAYMENT_GATEWAY_MODE","disabled")=="live"
    paid=live and CentralPayment.objects.filter(transaction_status="captured").exists()
    statuses={"tenants":"connected","identity":"connected" if sso else "planned","marketplace":"connected" if resources else "planned",
        "pricing":"connected" if pricing else "planned","payments":"connected" if paid else "mock" if settings.PAYMENT_GATEWAY_MODE=="mock" else "planned",
        "billing":"connected" if paid else "planned","analytics":"connected","notifications":"planned","privacy":"planned"}
    return JsonResponse({"checkedAt":timezone.now().isoformat(),"statuses":statuses,
        "note":"Connected reflects observed API activity; it is not a production readiness certification."})
