from functools import wraps
import time

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect

from .services import user_has_permission


def _deny(request):
    if request.path.startswith("/api/"):
        return JsonResponse({"detail": "Permission denied."}, status=403)
    return redirect("dashboard")


def _client_ip(request):
    forwarded = (request.META.get("HTTP_X_FORWARDED_FOR") or "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    return (request.META.get("REMOTE_ADDR") or "").strip()


def _log_sensitive_access(request, permission_code, status, reason=""):
    try:
        from .models import SensitiveAccessEvent

        SensitiveAccessEvent.objects.create(
            user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
            permission_code=permission_code,
            path=(request.path or "")[:255],
            ip_address=_client_ip(request)[:64],
            user_agent=(request.META.get("HTTP_USER_AGENT", "") or "")[:255],
            status=status,
            reason=(reason or "")[:255],
        )
    except Exception:
        return None


def require_permission(permission_code):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return _deny(request)
            if not user_has_permission(request.user, permission_code):
                return _deny(request)
            sensitive_prefixes = tuple(
                getattr(
                    settings,
                    "TWO_FACTOR_PROTECTED_PERMISSION_PREFIXES",
                    ("billing.", "commission.", "ops.", "pricing."),
                )
            )
            if permission_code.startswith(sensitive_prefixes):
                if not request.session.get("two_factor_verified", False):
                    _log_sensitive_access(
                        request,
                        permission_code,
                        "challenge",
                        "two_factor_required",
                    )
                    if request.path.startswith("/api/"):
                        return JsonResponse({"detail": "Two-factor verification required."}, status=403)
                    return redirect("two-factor-verify")
                verified_at = int(request.session.get("two_factor_verified_at") or 0)
                max_age = int(getattr(settings, "TWO_FACTOR_PRIVILEGED_SESSION_SECONDS", 1800))
                if verified_at <= 0 or (time.time() - verified_at) > max_age:
                    request.session["two_factor_verified"] = False
                    request.session["two_factor_verified_at"] = 0
                    _log_sensitive_access(
                        request,
                        permission_code,
                        "challenge",
                        "two_factor_session_expired",
                    )
                    if request.path.startswith("/api/"):
                        return JsonResponse({"detail": "Two-factor session expired."}, status=403)
                    return redirect("two-factor-verify")
                reauth_prefixes = tuple(
                    getattr(
                        settings,
                        "REAUTH_PROTECTED_PERMISSION_PREFIXES",
                        ("billing.", "commission."),
                    )
                )
                if permission_code.startswith(reauth_prefixes):
                    reauth_at = int(request.session.get("reauth_verified_at") or 0)
                    reauth_max_age = int(getattr(settings, "REAUTH_SESSION_SECONDS", 900))
                    if reauth_at <= 0 or (time.time() - reauth_at) > reauth_max_age:
                        request.session["reauth_verified_at"] = 0
                        _log_sensitive_access(
                            request,
                            permission_code,
                            "challenge",
                            "reauth_required",
                        )
                        if request.path.startswith("/api/"):
                            return JsonResponse({"detail": "Re-authentication required."}, status=403)
                        return redirect(f"/accounts/reauth/?next={request.get_full_path()}")
                _log_sensitive_access(request, permission_code, "granted", "")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
