import hashlib
import json
from urllib.parse import urlencode, urlsplit
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import F
from .models import CustomerTokenVersion
from django.http import JsonResponse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

MESSAGE = "If an eligible account exists, a password reset link will be emailed."

def body(request):
    value = json.loads(request.body)
    if not isinstance(value, dict):
        raise ValueError("Expected an object")
    return value

@csrf_exempt
@require_POST
def request_reset(request):
    try:
        data = body(request)
        email = str(data.get("email") or "").strip().lower()
        validate_email(email)
    except (ValueError, TypeError, UnicodeDecodeError, ValidationError):
        return JsonResponse({"detail": "Enter a valid email address."}, status=400)
    origin = str(getattr(settings, "NEXIVO_PUBLIC_URL", "http://localhost:3000")).rstrip("/")
    parsed = urlsplit(origin)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or (getattr(settings, "IS_PRODUCTION", False) and parsed.scheme != "https"):
        return JsonResponse({"detail": "Password recovery is not configured."}, status=503)
    # Same response for unknown, inactive, unusable-password and throttled accounts.
    key = "password-reset:" + hashlib.sha256(email.encode()).hexdigest()
    if cache.add(key, 1, timeout=60):
        for user in PasswordResetForm().get_users(email):
            query = urlencode({"uid": urlsafe_base64_encode(force_bytes(user.pk)), "token": default_token_generator.make_token(user)})
            link = f"{origin}/reset-password?{query}"
            send_mail("Reset your Nexivo password", f"Use this link to reset your password:\n\n{link}\n\nIf you did not request this, ignore this email.", settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    return JsonResponse({"detail": MESSAGE})

@csrf_exempt
@require_POST
def confirm_reset(request):
    try:
        data = body(request)
        uid = force_str(urlsafe_base64_decode(str(data.get("uid") or "")))
        password = str(data.get("password") or "")
        if not password or len(password) < 8:
            raise ValidationError("Use at least eight characters for your new password.")
        with transaction.atomic():
            user = get_user_model().objects.select_for_update().get(pk=uid, is_active=True)
            if not default_token_generator.check_token(user, str(data.get("token") or "")):
                return JsonResponse({"detail": "This reset link is invalid or expired."}, status=400)
            validate_password(password, user)
            user.set_password(password)
            user.save(update_fields=["password"])
            version, _ = CustomerTokenVersion.objects.get_or_create(user=user)
            CustomerTokenVersion.objects.filter(pk=version.pk).update(version=F("version") + 1)
    except ValidationError as exc:
        return JsonResponse({"detail": " ".join(exc.messages)}, status=400)
    except (ValueError, TypeError, UnicodeDecodeError, OverflowError, get_user_model().DoesNotExist):
        return JsonResponse({"detail": "This reset link is invalid or expired."}, status=400)
    return JsonResponse({"detail": "Password updated. You can now sign in."})
