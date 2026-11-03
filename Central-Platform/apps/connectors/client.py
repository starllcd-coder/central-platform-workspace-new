import hashlib
import hmac
import json
import os
import time
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from django.conf import settings
from .models import AppConnector

class ProviderUnavailable(ValueError): pass

def provider_url(tenant, module, kind):
    connector = AppConnector.objects.filter(tenant=tenant,module=module,is_active=True).first()
    if not connector:
        connector=AppConnector.objects.filter(tenant__isnull=True,module=module,is_active=True).first()
    base=connector.base_url if connector else ""
    if not base:
        configured=os.getenv(f"{module.code.upper()}_CONNECTOR_URL", "")
        suffix="/orders/central/webhook/" if module.code=="laundrex" else "/api/central/bookings/"
        base=configured.removesuffix(suffix)
    if not base: raise ProviderUnavailable("Provider connection is not configured.")
    prefix="/orders/central/" if module.code=="laundrex" else "/api/central/"
    return base.rstrip("/")+prefix+kind+"/"

def provider_request(tenant,module,kind,payload):
    raw=json.dumps(payload,default=str).encode()
    ts=str(int(time.time()));nonce=uuid.uuid4().hex
    secret=settings.CONNECTOR_SHARED_SECRET
    signature=hmac.new(secret.encode(),f"{ts}.{nonce}.".encode()+raw,hashlib.sha256).hexdigest()
    req=Request(provider_url(tenant,module,kind),data=raw,method="POST",headers={
        "Content-Type":"application/json","X-Connector-Secret":secret,"X-Tenant-Code":tenant.tenant_code,
        "X-Connector-Timestamp":ts,"X-Connector-Nonce":nonce,"X-Connector-Signature":signature})
    try:
        with urlopen(req,timeout=10) as response: result=json.loads(response.read())
    except HTTPError as exc:
        try: detail=json.loads(exc.read()).get("error","Provider rejected the request.")
        except Exception: detail="Provider rejected the request."
        if exc.code>=500: raise ProviderUnavailable(detail) from exc
        raise ValueError(detail) from exc
    except (URLError,TimeoutError,OSError) as exc:
        raise ProviderUnavailable("The provider is temporarily unavailable.") from exc
    if not isinstance(result,dict) or result.get("ok") is not True:
        raise ValueError("Provider did not acknowledge the request.")
    from .models import ConnectorHealthLog
    ConnectorHealthLog.objects.create(endpoint="provider."+kind,tenant=tenant,module=module,status_code=200,is_success=True,auth_key_version="active")
    return result
