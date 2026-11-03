from django.core import signing
from django.conf import settings
from django.db.models import Q

from .models import MembershipRole, RolePermission, TenantMembership


def issue_sso_token(payload):
    return signing.dumps(payload, salt="central-sso-v1")


def validate_sso_token(token, max_age=3600):
    return signing.loads(token, salt="central-sso-v1", max_age=max_age)


def get_user_permission_codes(user_id, tenant_id=None, module_code=None):
    membership_filter = Q(membership__user_id=user_id, membership__status="active")
    if tenant_id is not None:
        membership_filter &= Q(membership__tenant_id=tenant_id)

    role_ids = MembershipRole.objects.filter(membership_filter).values_list("role_id", flat=True)
    permissions = RolePermission.objects.filter(role_id__in=role_ids).select_related(
        "permission", "permission__module"
    )

    codes = []
    for item in permissions:
        permission = item.permission
        if not permission.is_active:
            continue
        if module_code and permission.module and permission.module.code != module_code:
            continue
        codes.append(permission.code)
    return sorted(set(codes))


def user_in_tenant(user_id, tenant_id):
    return TenantMembership.objects.filter(
        user_id=user_id, tenant_id=tenant_id, status="active"
    ).exists()


def user_permission_codes(user):
    if not user or not user.is_authenticated:
        return set()
    if user.is_superuser:
        return {"*"}
    return set(get_user_permission_codes(user_id=user.id))


def user_has_permission(user, permission_code):
    perms = user_permission_codes(user)
    return "*" in perms or permission_code in perms


def get_user_tenant_ids(user):
    if not user or not user.is_authenticated:
        return []
    if user.is_superuser:
        from apps.tenants.models import Tenant

        return list(Tenant.objects.values_list("id", flat=True))
    return list(
        TenantMembership.objects.filter(user=user, status="active").values_list(
            "tenant_id", flat=True
        )
    )


def get_accessible_tenants(user):
    from apps.tenants.models import Tenant

    if not user or not user.is_authenticated:
        return Tenant.objects.none()
    if user.is_superuser:
        return Tenant.objects.all().order_by("name")
    return Tenant.objects.filter(id__in=get_user_tenant_ids(user)).order_by("name")


def user_can_access_tenant(user, tenant_id):
    if not tenant_id:
        return False
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return TenantMembership.objects.filter(
        user=user, tenant_id=tenant_id, status="active"
    ).exists()


def get_accessible_modules(user, tenant=None):
    from apps.tenants.models import Module, TenantModule

    if not user or not user.is_authenticated:
        return Module.objects.none()

    if user.is_superuser:
        if tenant is not None:
            return Module.objects.filter(
                is_active=True,
                tenant_modules__tenant=tenant,
                tenant_modules__enabled=True,
            ).distinct().order_by("name")
        return Module.objects.filter(is_active=True).order_by("name")

    tenant_ids = get_user_tenant_ids(user)
    if tenant is not None:
        tenant_ids = [tenant.id] if tenant.id in tenant_ids else []
    module_ids = TenantModule.objects.filter(
        tenant_id__in=tenant_ids,
        enabled=True,
    ).values_list("module_id", flat=True)
    return Module.objects.filter(id__in=module_ids, is_active=True).distinct().order_by("name")


def user_can_access_module(user, module_id, tenant=None):
    if not module_id:
        return False
    return get_accessible_modules(user, tenant=tenant).filter(id=module_id).exists()


def user_requires_mandatory_2fa(user):
    if not user or not user.is_authenticated:
        return False
    if getattr(settings, "TWO_FACTOR_MANDATORY_FOR_SUPERUSER", True) and user.is_superuser:
        return True
    must_perms = set(getattr(settings, "TWO_FACTOR_MANDATORY_PERMISSION_CODES", ()))
    if not must_perms:
        return False
    user_perms = user_permission_codes(user)
    return bool(must_perms.intersection(user_perms))
