from apps.tenants.models import Module, Tenant, TenantBranding

from .services import (
    get_accessible_modules,
    get_accessible_tenants,
    user_can_access_module,
    user_can_access_tenant,
)


class TenantContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.active_tenant = None
        request.active_module = None
        request.host_matched_tenant = None

        host = (request.get_host() or "").split(":")[0].strip().lower().rstrip(".")
        if host:
            host_branding = (
                TenantBranding.objects.select_related("tenant")
                .filter(
                    is_active=True,
                    custom_domain__iexact=host,
                    domain_verification_status="verified",
                )
                .first()
            )
            if host_branding is not None:
                request.host_matched_tenant = host_branding.tenant

        if request.user.is_authenticated:
            tenant_id = None

            if request.host_matched_tenant and user_can_access_tenant(
                request.user, request.host_matched_tenant.id
            ):
                tenant_id = request.host_matched_tenant.id
                request.session["active_tenant_id"] = tenant_id

            query_tid = request.GET.get("tenant_id")
            if tenant_id is None and query_tid and query_tid.isdigit():
                tenant_id = int(query_tid)
                if user_can_access_tenant(request.user, tenant_id):
                    request.session["active_tenant_id"] = tenant_id

            if tenant_id is None:
                session_tid = request.session.get("active_tenant_id")
                if isinstance(session_tid, int) and user_can_access_tenant(
                    request.user, session_tid
                ):
                    tenant_id = session_tid

            if tenant_id is None:
                header_code = request.headers.get("X-Tenant-Code", "").strip()
                if header_code:
                    tenant = Tenant.objects.filter(tenant_code=header_code).first()
                    if tenant and user_can_access_tenant(request.user, tenant.id):
                        tenant_id = tenant.id
                        request.session["active_tenant_id"] = tenant_id

            if tenant_id:
                request.active_tenant = Tenant.objects.filter(pk=tenant_id).first()
            elif request.user.is_superuser or request.user.is_authenticated:
                first = get_accessible_tenants(request.user).first()
                if first:
                    request.active_tenant = first
                    request.session["active_tenant_id"] = first.id

            module_id = None
            query_mid = request.GET.get("module_id")
            if query_mid and query_mid.isdigit():
                module_id = int(query_mid)
                if user_can_access_module(
                    request.user,
                    module_id,
                    tenant=request.active_tenant,
                ):
                    request.session["active_module_id"] = module_id
                else:
                    module_id = None

            if module_id is None:
                session_mid = request.session.get("active_module_id")
                if isinstance(session_mid, int) and user_can_access_module(
                    request.user,
                    session_mid,
                    tenant=request.active_tenant,
                ):
                    module_id = session_mid

            if module_id:
                request.active_module = Module.objects.filter(pk=module_id, is_active=True).first()

        return self.get_response(request)
