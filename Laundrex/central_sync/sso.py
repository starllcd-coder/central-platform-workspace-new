import json
import secrets
import time
from urllib.parse import urlencode
from django.shortcuts import redirect
from urllib.request import Request,urlopen
from django.conf import settings
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST,require_GET
from .models import CentralAccountLink

@csrf_exempt
@require_POST
def consume_ticket(request):
    if not getattr(settings,"CENTRAL_SSO_ENABLED",False):return JsonResponse({"error":"Central sign-in is not enabled."},status=503)
    try:
        body=json.loads(request.body)
        token=str(body.get("token") or "")
        if not token or len(token)>10000:raise ValueError("Invalid login ticket.")
        base=settings.CENTRAL_PLATFORM_URL.rstrip("/")
        if not settings.DEBUG and not base.startswith("https://"):raise ValueError("Central sign-in requires HTTPS.")
        req=Request(base+"/accounts/api/sso/introspect/",data=json.dumps({"token":token,"consume":True}).encode(),method="POST",
            headers={"Content-Type":"application/json","X-Connector-Secret":settings.CENTRAL_CONNECTOR_SECRET})
        with urlopen(req,timeout=10) as response:verified=json.loads(response.read())
        claims=verified.get("claims",{})
        if verified.get("active") is not True or claims.get("kind")!="login-ticket" or claims.get("tenant_code")!=settings.CENTRAL_TENANT_CODE or settings.CENTRAL_MODULE_CODE not in claims.get("module_codes",[]):raise ValueError("Login ticket is invalid, expired, or intended for another app.")
        state=request.session.get("central_sso_state","")
        if not state or not secrets.compare_digest(state,str(claims.get("state") or "")) or time.time()>request.session.get("central_sso_deadline",0):raise ValueError("App login state did not match.")
        link=CentralAccountLink.objects.select_related("user").filter(central_user_id=str(claims.get("uid")),is_active=True,user__is_active=True).first()
        if not link:raise ValueError("Ask the app administrator to link your existing account.")
        from .sso_context import context_for
        session_values=context_for(link.user)
        request.session.pop("central_sso_state",None)
        request.session.pop("central_sso_deadline",None)
        login(request,link.user,backend="django.contrib.auth.backends.ModelBackend")
        for key,value in session_values.items():request.session[key]=value
        request.session.set_expiry(0)
        return JsonResponse({"ok":True,"redirect":"/"})
    except Exception:
        return JsonResponse({"error":"Central sign-in could not be completed. Your normal app login is still available."},status=403)


@require_GET
def begin_login(request):
    if not getattr(settings,"CENTRAL_SSO_ENABLED",False):return JsonResponse({"error":"Central sign-in is not enabled."},status=503)
    origin=getattr(settings,"CENTRAL_NEXIVO_URL","http://localhost:3000").rstrip("/")
    if not origin.startswith("https://") and not settings.DEBUG:return JsonResponse({"error":"A secure broker URL is required."},status=503)
    state=secrets.token_urlsafe(32)
    request.session["central_sso_state"]=state;request.session["central_sso_deadline"]=time.time()+300
    return redirect(origin+"/partner/app-launch?"+urlencode({"state":state,"tenantCode":settings.CENTRAL_TENANT_CODE,"moduleCode":settings.CENTRAL_MODULE_CODE}))
