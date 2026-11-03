from decimal import Decimal
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_GET
from apps.accounts.models import TenantMembership, MembershipRole, RolePermission
from apps.tenants.models import MarketplaceListing, Tenant, DemoTenantRequest
from apps.billing.models import CommissionInvoice
from apps.connectors.models import ConnectorEvent, ConnectorHealthLog, AppConnector
from apps.ops.models import AuditLog
from .models import MarketplaceBooking

PRODUCTS={"staylux":"StayLux","drivesphere":"DriveSphere","laundrex":"Laundrex"}

def scope(user, permission="marketplace.view"):
    if user.is_superuser:return Q()
    result=Q(pk__in=[])
    roles=MembershipRole.objects.filter(membership__user=user,membership__status="active",role__is_active=True).select_related("membership","module","role")
    for role in roles:
        if role.role.code!="tenant.owner" and not RolePermission.objects.filter(role=role.role,permission__code=permission,permission__is_active=True).exists():continue
        part=Q(tenant_id=role.membership.tenant_id)
        if role.module_id:part &= Q(module_id=role.module_id)
        result |= part
    return result

def owner_tenants(user):
    if user.is_superuser:return Tenant.objects.values_list("pk",flat=True)
    return MembershipRole.objects.filter(membership__user=user,membership__status="active",role__code="tenant.owner",role__is_active=True,module__isnull=True).values_list("membership__tenant_id",flat=True)

def gross(rows):
    return ", ".join(f"{row['amount'] or 0} {row['currency']}" for row in rows.exclude(status__in=["failed","cancelled"]).values("currency").annotate(amount=Sum("total_amount"))) or "0"

@require_GET
def partner_dashboard(request):
    from .views import _auth_customer
    user=_auth_customer(request)
    if not user or not user.is_active:return JsonResponse({"detail":"Unauthorized."},status=401)
    from .sso import privileged_mfa_ok
    if not privileged_mfa_ok(request,user):return JsonResponse({"detail":"Two-factor verification required."},status=403)
    bookings=MarketplaceBooking.objects.filter(scope(user)).select_related("module","tenant")
    listings=MarketplaceListing.objects.filter(scope(user)).select_related("module","tenant")
    owners=owner_tenants(user)
    invoices=CommissionInvoice.objects.filter(tenant_id__in=owners)
    memberships=TenantMembership.objects.filter(tenant_id__in=owners).select_related("user")
    modules={tenant.pk:list(tenant.tenant_modules.filter(enabled=True).values_list("module__code",flat=True)) for tenant in Tenant.objects.filter(pk__in=owners)}
    metrics=[{"label":"Bookings","value":str(bookings.count()),"description":"Current marketplace bookings and service orders."},
        {"label":"Active Listings","value":str(listings.filter(is_active=True).count()),"description":"Published provider resources."},
        {"label":"Gross Booking Value","value":gross(bookings),"description":"Excludes cancelled and failed bookings; not a payout balance."},
        {"label":"Cancelled","value":str(bookings.filter(status="cancelled").count()),"description":"Cancelled marketplace bookings."}]
    return JsonResponse({
        "launches":[{"tenantCode":r.tenant.tenant_code,"moduleCode":r.module.code,"name":r.module.name} for r in AppConnector.objects.filter(scope(user),is_active=True).exclude(public_url="").select_related("tenant","module") if r.tenant_id],
        "metrics":metrics,"activeListings":listings.filter(is_active=True).count(),"bookingCount":bookings.count(),"gross":gross(bookings),
        "bookings":[{"id":r.booking_id,"product":r.module.code,"customer":r.customer_name,"service":r.listing.provider_resource_name if r.listing else r.module.name,
            "date":r.created_at.date().isoformat(),"amount":f"{r.total_amount} {r.currency}","status":r.status if r.status in {"confirmed","completed","cancelled"} else "pending"} for r in bookings[:500]],
        "listings":[{"id":str(r.pk),"product":r.module.code,"title":r.provider_resource_name or r.tenant.name,"location":r.snapshot.get("city") or r.tenant.country,
            "status":"active" if r.is_active else "paused","views":0,"bookings":r.marketplace_bookings.count(),"revenue":gross(r.marketplace_bookings.all())} for r in listings[:500]],
        "invoices":[{"id":r.code,"title":r.code,"amount":f"{r.amount_due} {r.currency}","dueDate":r.due_date.isoformat(),"status":"unpaid" if r.status=="pending" else r.status} for r in invoices[:500]],
        "staff":[{"id":str(r.pk),"name":r.user.get_full_name() or r.user.username,"email":r.user.email,"role":", ".join(r.membership_roles.values_list("role__name",flat=True)),
            "productAccess":[code for code in modules.get(r.tenant_id,[]) if code in PRODUCTS],"status":"disabled" if r.status=="suspended" else r.status} for r in memberships[:500]],
    })

@require_GET
def admin_dashboard(request):
    from .views import _auth_customer
    user=_auth_customer(request)
    if not user or not user.is_active:return JsonResponse({"detail":"Unauthorized."},status=401)
    from .sso import privileged_mfa_ok
    if not privileged_mfa_ok(request,user):return JsonResponse({"detail":"Two-factor verification required."},status=403)
    if not user.is_superuser:return JsonResponse({"detail":"Administrator access required."},status=403)
    bookings=MarketplaceBooking.objects.all()
    checked=timezone.now().isoformat()
    failures=ConnectorEvent.objects.filter(status__in=["dead_letter","dispatch_failed"]).count()
    return JsonResponse({"metrics":[
        {"label":"Marketplace Bookings","value":str(bookings.count()),"description":"Current marketplace requests.","trend":"stable"},
        {"label":"Gross Booking Value","value":gross(bookings),"description":"Excludes failed/cancelled bookings.","trend":"stable"},
        {"label":"Business Leads","value":str(DemoTenantRequest.objects.count()),"description":"Business onboarding requests.","trend":"stable"},
        {"label":"Active Partners","value":str(Tenant.objects.filter(status="active").count()),"description":"Active Central tenants.","trend":"stable"}],
        "products":[{"product":name,"bookings":bookings.filter(module__code=code).count(),"revenue":gross(bookings.filter(module__code=code)),
            "activeListings":MarketplaceListing.objects.filter(module__code=code,is_active=True).count(),"conversionRate":"Not tracked"} for code,name in PRODUCTS.items()],
        "monitoring":[{"id":"central-connectors","name":"Booking delivery queue","area":"central-platform","status":"warning" if failures else "healthy",
            "uptime":"Not measured","latency":"Not measured","lastChecked":checked}],
        "auditLogs":[{"id":str(r.pk),"action":"integration-sync","actor":r.actor.username if r.actor else "system","actorRole":"admin" if r.actor else "system",
            "target":f"{r.entity_type}:{r.entity_id}","description":r.action,"ipAddress":"Not recorded","createdAt":r.created_at.isoformat()} for r in AuditLog.objects.select_related("actor")[:200]],
        "auditCount":AuditLog.objects.count(),"reports":[],"systemStatus":"Attention required" if failures else "Available"})
