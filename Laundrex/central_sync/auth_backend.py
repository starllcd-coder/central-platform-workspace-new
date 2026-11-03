import json
from urllib.request import Request,urlopen
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import CentralAccountLink

class MappedCentralBackend(ModelBackend):
    """Optional shared credentials for existing linked local accounts; never provisions or changes roles."""
    def authenticate(self,request,username=None,password=None,**kwargs):
        if not getattr(settings,"CENTRAL_SSO_ENABLED",False) or not password:return None
        User=get_user_model();identifier=username or kwargs.get(User.USERNAME_FIELD) or kwargs.get("email")
        if not identifier:return None
        users=User.objects.filter(**{User.USERNAME_FIELD+"__iexact":identifier},is_active=True)
        if users.count()!=1:return None
        user=users.first()
        link=CentralAccountLink.objects.filter(user=user,is_active=True).first()
        if not link:return None
        base=settings.CENTRAL_PLATFORM_URL.rstrip("/")
        if not settings.DEBUG and not base.startswith("https://"):return None
        endpoint="/api/provider/login/" if user.is_staff or user.is_superuser else "/api/auth/login/"
        try:
            body={"email":user.email,"password":password,"otp":kwargs.get("otp","")}
            req=Request(base+endpoint,data=json.dumps(body).encode(),method="POST",headers={"Content-Type":"application/json"})
            with urlopen(req,timeout=5) as response:verified=json.loads(response.read())
            if str(verified.get("user",{}).get("id"))!=link.central_user_id:return None
            return user
        except Exception:return None
