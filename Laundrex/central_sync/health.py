import hmac
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import CentralAccountLink

@require_GET
def health(request):
    secret=getattr(settings,"CENTRAL_CONNECTOR_SECRET","")
    if not secret or not hmac.compare_digest(request.headers.get("X-Connector-Secret",""),secret):return JsonResponse({"detail":"Unauthorized."},status=403)
    return JsonResponse({"status":"ok","moduleCode":settings.CENTRAL_MODULE_CODE,"tenantCode":settings.CENTRAL_TENANT_CODE,
        "syncEnabled":settings.CENTRAL_SYNC_ENABLED,"ssoEnabled":settings.CENTRAL_SSO_ENABLED,
        "linkedAccounts":CentralAccountLink.objects.filter(is_active=True,user__is_active=True).count()})
