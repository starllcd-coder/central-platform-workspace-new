import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, PasswordResetConfirmView
from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.tenants.models import Tenant

from .models import TenantMembership, UserTwoFactor, UserTwoFactorBackupCode


class BusinessInvitationConfirmView(PasswordResetConfirmView):
    template_name = "registration/business_invitation_confirm.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        TenantMembership.objects.filter(user=self.user, status="invited").update(status="active")
        messages.success(self.request, "Your password is set. Sign in to access your business account.")
        return response
from .services import (
    get_accessible_modules,
    get_accessible_tenants,
    get_user_permission_codes,
    issue_sso_token,
    user_can_access_module,
    user_can_access_tenant,
    user_in_tenant,
    user_requires_mandatory_2fa,
    validate_sso_token,
)
from .twofa import backup_code_hash, generate_backup_codes, generate_base32_secret, verify_totp


def _regenerate_backup_codes(two_factor_row, count=8):
    plain_codes = generate_backup_codes(count=count)
    UserTwoFactorBackupCode.objects.filter(two_factor=two_factor_row).delete()
    UserTwoFactorBackupCode.objects.bulk_create(
        [
            UserTwoFactorBackupCode(two_factor=two_factor_row, code_hash=backup_code_hash(item))
            for item in plain_codes
        ]
    )
    return plain_codes


class RememberMeLoginView(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        remember_me = self.request.POST.get("remember_me")
        self.request.session["two_factor_verified"] = False
        self.request.session["two_factor_verified_at"] = 0
        if remember_me:
            self.request.session.set_expiry(getattr(settings, "SESSION_COOKIE_AGE", 1209600))
        else:
            self.request.session.set_expiry(0)
        response = super().form_valid(form)
        if user_requires_mandatory_2fa(self.request.user):
            row = UserTwoFactor.objects.filter(user=self.request.user, is_enabled=True).first()
            if row is None:
                return redirect("two-factor-setup")
            return redirect("two-factor-verify")
        return response


@login_required
@require_http_methods(["GET"])
def two_factor_setup(request):
    row, _ = UserTwoFactor.objects.get_or_create(user=request.user)
    if not row.secret:
        row.secret = generate_base32_secret()
        row.save(update_fields=["secret", "updated_at"])
    backup_codes = request.session.pop("two_factor_backup_codes", None)
    return render(
        request,
        "registration/two_factor_setup.html",
        {
            "two_factor": row,
            "issuer": getattr(settings, "TWO_FACTOR_ISSUER", "CentralPlatform"),
            "backup_codes": backup_codes,
        },
    )


@login_required
@require_http_methods(["GET", "POST"])
def two_factor_verify(request):
    row = UserTwoFactor.objects.filter(user=request.user, is_enabled=True).first()
    if row is None:
        messages.info(request, "Two-factor is not enabled yet. Configure it first.")
        return redirect("two-factor-setup")

    if request.method == "POST":
        code = request.POST.get("code", "")
        verified = verify_totp(row.secret, code)
        if not verified:
            normalized_hash = backup_code_hash(code)
            backup = (
                UserTwoFactorBackupCode.objects.filter(
                    two_factor=row,
                    code_hash=normalized_hash,
                    is_used=False,
                )
                .order_by("id")
                .first()
            )
            if backup is not None:
                backup.is_used = True
                backup.used_at = timezone.now()
                backup.save(update_fields=["is_used", "used_at"])
                verified = True
                messages.warning(request, "Backup code used. Generate new backup codes soon.")

        if verified:
            row.last_verified_at = timezone.now()
            row.save(update_fields=["last_verified_at", "updated_at"])
            request.session["two_factor_verified"] = True
            request.session["two_factor_verified_at"] = int(timezone.now().timestamp())
            messages.success(request, "Two-factor verification completed.")
            next_url = request.POST.get("next") or request.GET.get("next") or "dashboard"
            return redirect(next_url)
        messages.error(request, "Invalid verification code.")

    return render(request, "registration/two_factor_verify.html", {"two_factor": row})


@login_required
@require_http_methods(["POST"])
def two_factor_enable(request):
    row, _ = UserTwoFactor.objects.get_or_create(user=request.user)
    if not row.secret:
        row.secret = generate_base32_secret()
    code = request.POST.get("code", "")
    if not verify_totp(row.secret, code):
        messages.error(request, "Invalid verification code.")
        return redirect("two-factor-setup")
    row.is_enabled = True
    row.last_verified_at = timezone.now()
    row.save(update_fields=["secret", "is_enabled", "last_verified_at", "updated_at"])
    codes = _regenerate_backup_codes(row)
    request.session["two_factor_backup_codes"] = codes
    request.session["two_factor_verified"] = True
    request.session["two_factor_verified_at"] = int(timezone.now().timestamp())
    messages.success(request, "Two-factor has been enabled. Save your backup codes now.")
    return redirect("two-factor-setup")


@login_required
@require_http_methods(["POST"])
def two_factor_regenerate_backup_codes(request):
    row = UserTwoFactor.objects.filter(user=request.user, is_enabled=True).first()
    if row is None:
        messages.error(request, "Enable two-factor first.")
        return redirect("two-factor-setup")
    code = request.POST.get("code", "")
    if not verify_totp(row.secret, code):
        messages.error(request, "Invalid verification code.")
        return redirect("two-factor-setup")
    codes = _regenerate_backup_codes(row)
    request.session["two_factor_backup_codes"] = codes
    messages.success(request, "Backup codes regenerated.")
    return redirect("two-factor-setup")


@login_required
@require_http_methods(["GET", "POST"])
def reauth_verify(request):
    if request.method == "POST":
        password = request.POST.get("password", "")
        if request.user.check_password(password):
            request.session["reauth_verified_at"] = int(timezone.now().timestamp())
            messages.success(request, "Re-authentication completed.")
            next_url = request.POST.get("next") or request.GET.get("next") or "dashboard"
            return redirect(next_url)
        messages.error(request, "Invalid password.")
    return render(request, "registration/reauth_verify.html")


def _connector_authorized(request):
    expected = getattr(settings, "CONNECTOR_SHARED_SECRET", "dev-connector-secret")
    provided = request.headers.get("X-Connector-Secret", "")
    return bool(expected) and (provided == expected)


@csrf_exempt
@require_http_methods(["POST"])
@login_required
def sso_token_issue_api(request):
    if not request.user.is_staff:
        return JsonResponse({"detail": "Staff access required."}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else {}
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    user_id = payload.get("user_id", request.user.id)
    tenant_id = payload.get("tenant_id")
    module_codes = payload.get("module_codes", [])

    if tenant_id is None:
        return JsonResponse({"detail": "tenant_id is required."}, status=400)

    try:
        tenant = Tenant.objects.get(pk=tenant_id)
    except Tenant.DoesNotExist:
        return JsonResponse({"detail": "tenant_id not found."}, status=404)

    if not user_in_tenant(user_id, tenant.id):
        return JsonResponse({"detail": "User is not active in this tenant."}, status=400)

    permissions = get_user_permission_codes(user_id=user_id, tenant_id=tenant.id)
    token_payload = {
        "uid": user_id,
        "tenant_id": tenant.id,
        "tenant_code": tenant.tenant_code,
        "module_codes": module_codes,
        "permissions": permissions,
    }
    token = issue_sso_token(token_payload)
    return JsonResponse(
        {
            "token": token,
            "token_type": "central-sso",
            "expires_in": getattr(settings, "SSO_TOKEN_MAX_AGE", 3600),
            "claims": token_payload,
        }
    )


@csrf_exempt
@require_http_methods(["POST"])
def sso_token_introspect_api(request):
    if not _connector_authorized(request):
        return JsonResponse({"detail": "Connector authorization failed."}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    token = payload.get("token")
    if not token:
        return JsonResponse({"active": False, "detail": "token is required"}, status=400)

    try:
        claims = validate_sso_token(token, max_age=getattr(settings, "SSO_TOKEN_MAX_AGE", 3600))
    except Exception:
        return JsonResponse({"active": False})

    from django.contrib.auth import get_user_model
    from apps.marketplace.models import CustomerTokenVersion
    user = get_user_model().objects.filter(pk=claims.get("uid"),is_active=True).first()
    if not user or (not user.is_superuser and not user_in_tenant(user.pk,claims.get("tenant_id"))):
        return JsonResponse({"active":False})
    if claims.get("kind") == "login-ticket":
        from apps.tenants.models import TenantModule
        if not TenantModule.objects.filter(tenant_id=claims.get("tenant_id"), module__code__in=claims.get("module_codes",[]),enabled=True).exists():
            return JsonResponse({"active":False})
        import time
        from apps.connectors.models import ConnectorRequestNonce
        from django.db import IntegrityError, transaction
        version = CustomerTokenVersion.objects.filter(user=user).values_list("version",flat=True).first() or 0
        if claims.get("exp",0) < time.time() or claims.get("version",0) != version:
            return JsonResponse({"active":False})
        if payload.get("consume") is True:
            try:
                with transaction.atomic():
                    ConnectorRequestNonce.objects.create(nonce="sso:"+claims["jti"],event_type="sso.consume")
            except IntegrityError:
                return JsonResponse({"active":False})
    claims["email"] = user.email
    permissions = get_user_permission_codes(
        user_id=claims.get("uid"),
        tenant_id=claims.get("tenant_id"),
    )
    claims["permissions"] = permissions
    return JsonResponse({"active": True, "claims": claims})


@login_required
@require_http_methods(["POST"])
def switch_tenant(request):
    tenant_id = request.POST.get("tenant_id")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"

    if tenant_id and tenant_id.isdigit():
        tenant_id_int = int(tenant_id)
        if user_can_access_tenant(request.user, tenant_id_int):
            request.session["active_tenant_id"] = tenant_id_int
        else:
            first = get_accessible_tenants(request.user).first()
            request.session["active_tenant_id"] = first.id if first else None

    return redirect(next_url)


@login_required
@require_http_methods(["POST"])
def switch_module(request):
    module_id = request.POST.get("module_id")
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
    active_tenant = getattr(request, "active_tenant", None)

    if module_id == "all":
        request.session["active_module_id"] = None
        return redirect(next_url)

    if module_id and module_id.isdigit():
        module_id_int = int(module_id)
        if user_can_access_module(request.user, module_id_int, tenant=active_tenant):
            request.session["active_module_id"] = module_id_int
        else:
            first = get_accessible_modules(request.user, tenant=active_tenant).first()
            request.session["active_module_id"] = first.id if first else None

    return redirect(next_url)
