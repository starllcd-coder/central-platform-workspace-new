from .services import (
    get_accessible_modules,
    get_accessible_tenants,
    get_user_tenant_ids,
    user_permission_codes,
)
from apps.tenants.models import TenantBranding


def permission_context(request):
    perms = user_permission_codes(request.user)
    tenant_ids = get_user_tenant_ids(request.user)
    active_tenant = getattr(request, "active_tenant", None)
    active_module = getattr(request, "active_module", None)
    username = request.user.username if getattr(request.user, "is_authenticated", False) else ""
    initials = "".join([part[0].upper() for part in username.split()[:2] if part]) or (
        username[:2].upper() if username else "U"
    )
    if "*" in perms:
        role_label = "Super Admin"
    elif "billing.settle" in perms and "reports.view" in perms:
        role_label = "Operations Manager"
    elif "tenants.manage" in perms:
        role_label = "Tenant Manager"
    elif "reports.view" in perms:
        role_label = "Analyst"
    else:
        role_label = "Team Member"
    active_branding = None
    if active_tenant is not None:
        active_branding = TenantBranding.objects.filter(
            tenant=active_tenant,
            is_active=True,
        ).first()
    return {
        "permission_codes": perms,
        "is_super_admin": "*" in perms,
        "active_tenant": active_tenant,
        "active_module": active_module,
        "user_role_label": role_label,
        "user_avatar_initials": initials,
        "accessible_tenant_ids": tenant_ids,
        "accessible_tenants": get_accessible_tenants(request.user),
        "accessible_modules": get_accessible_modules(request.user, tenant=active_tenant),
        "active_tenant_branding": active_branding,
    }
