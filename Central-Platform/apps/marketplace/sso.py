import json
import time
import uuid
from urllib.parse import urlsplit
from django.core import signing
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.accounts.models import TenantMembership, UserTwoFactor
from apps.accounts.services import issue_sso_token
from apps.connectors.models import AppConnector
from apps.tenants.models import TenantModule
from .models import CustomerTokenVersion

def privileged_mfa_ok(request,user):
    from django.conf import settings
    row=UserTwoFactor.objects.filter(user=user,is_enabled=True).first()
    if not row:
        from apps.accounts.services import user_requires_mandatory_2fa
        return not (getattr(settings,"IS_PRODUCTION",False) and user_requires_mandatory_2fa(user))
    claims=getattr(request,"marketplace_claims",{})
    return claims.get("mfa") is True and time.time()-claims.get("mfa_at",0)<=getattr(settings,"TWO_FACTOR_PRIVILEGED_SESSION_SECONDS",1800)

@csrf_exempt
@require_POST
def ticket_api(request):
    from .views import _auth_customer
    user=_auth_customer(request)
    if not user:return JsonResponse({"detail":"Unauthorized."},status=401)
    if not privileged_mfa_ok(request,user):return JsonResponse({"detail":"Verify two-factor authentication before opening an app."},status=403)
    try:
        data=json.loads(request.body)
        binding=TenantModule.objects.select_related("tenant","module").filter(tenant__tenant_code=data.get("tenantCode"),module__code=data.get("moduleCode"),enabled=True).first()
        if not binding:raise ValueError("App access is unavailable.")
        if not user.is_superuser and not TenantMembership.objects.filter(user=user,tenant=binding.tenant,status="active").exists():raise ValueError("Tenant access is not active.")
        connector=AppConnector.objects.filter(tenant=binding.tenant,module=binding.module,is_active=True).first()
        if not connector or not connector.public_url:raise ValueError("The public app URL has not been configured.")
        url=connector.public_url.rstrip("/");parts=urlsplit(url)
        from django.conf import settings
        if parts.scheme not in {"http","https"} or not parts.hostname or parts.username or parts.password or (getattr(settings,"IS_PRODUCTION",False) and parts.scheme!="https"):raise ValueError("Invalid public app URL.")
        prefix = "/orders/central/sso/begin/" if binding.module.code=="laundrex" else "/api/central/sso/begin/"
        state=str(data.get("state") or "")
        if not state:return JsonResponse({"beginUrl":url+prefix})
        if len(state)<32 or len(state)>128:raise ValueError("Invalid app login state.")
        version=CustomerTokenVersion.objects.filter(user=user).values_list("version",flat=True).first() or 0
        token=issue_sso_token({"uid":user.pk,"email":user.email,"tenant_id":binding.tenant_id,"tenant_code":binding.tenant.tenant_code,
            "module_codes":[binding.module.code],"kind":"login-ticket","state":state,"jti":uuid.uuid4().hex,"exp":int(time.time())+60,"version":version})
        login_path="/accounts/login/" if binding.module.code=="laundrex" else "/login/"
        return JsonResponse({"launchUrl":url+login_path+"#central_sso="+token,"expiresIn":60})
    except (ValueError,TypeError,AttributeError) as exc:return JsonResponse({"detail":str(exc)},status=403)
