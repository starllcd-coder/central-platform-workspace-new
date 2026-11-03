from datetime import datetime, timedelta

from django.core.paginator import Paginator
from django.utils import timezone

DISPUTE_SORT_FIELDS = {
    "opened_at": "opened_at",
    "status": "status",
    "tenant": "tenant__name",
    "code": "code",
}

DISPUTE_PRIORITY_CHOICES = {"high", "attention", "normal"}


def parse_iso_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def dispute_urgency_meta(dispute):
    if dispute.status not in {"open", "under_review"} or not dispute.opened_at:
        return ("Normal", "off")
    age_hours = (timezone.now() - dispute.opened_at).total_seconds() / 3600
    if age_hours >= 48:
        return ("High", "danger")
    if age_hours >= 24:
        return ("Attention", "attention")
    return ("Normal", "pending")


def apply_dispute_filters_and_sort(disputes, request, active_module_id):
    selected_tenant_id = request.GET.get("tenant_id", "").strip()
    selected_status = request.GET.get("status", "").strip()
    selected_reason = request.GET.get("reason", "").strip()
    selected_q = request.GET.get("q", "").strip()
    opened_from = parse_iso_date(request.GET.get("opened_from"))
    opened_to = parse_iso_date(request.GET.get("opened_to"))
    selected_sort = request.GET.get("sort", "opened_at").strip()
    selected_order = request.GET.get("order", "desc").strip().lower()
    selected_priority = request.GET.get("priority", "").strip().lower()
    selected_module_id = request.GET.get("module_id", "").strip()
    has_explicit_sort = "sort" in request.GET or "order" in request.GET
    auto_triage_sort_applied = False

    if not selected_module_id and active_module_id:
        selected_module_id = str(active_module_id)

    if selected_tenant_id.isdigit():
        disputes = disputes.filter(tenant_id=int(selected_tenant_id))
    if selected_status == "pending":
        disputes = disputes.filter(status__in=["open", "under_review"])
        if not has_explicit_sort:
            selected_sort = "opened_at"
            selected_order = "asc"
            auto_triage_sort_applied = True
    elif selected_status in {"open", "under_review", "resolved", "rejected"}:
        disputes = disputes.filter(status=selected_status)
    if selected_reason in {"refund_delay", "wrong_charge", "service_issue", "other"}:
        disputes = disputes.filter(reason=selected_reason)
    if opened_from:
        disputes = disputes.filter(opened_at__date__gte=opened_from)
    if opened_to:
        disputes = disputes.filter(opened_at__date__lte=opened_to)
    if selected_q:
        disputes = disputes.filter(code__icontains=selected_q)
    if selected_module_id.isdigit():
        disputes = disputes.filter(transaction__module_id=int(selected_module_id))

    now = timezone.now()
    threshold_24h = now - timedelta(hours=24)
    threshold_48h = now - timedelta(hours=48)
    if selected_priority == "high":
        disputes = disputes.filter(status__in=["open", "under_review"], opened_at__lte=threshold_48h)
    elif selected_priority == "attention":
        disputes = disputes.filter(
            status__in=["open", "under_review"],
            opened_at__gt=threshold_48h,
            opened_at__lte=threshold_24h,
        )
    elif selected_priority == "normal":
        disputes = disputes.filter(status__in=["open", "under_review"], opened_at__gt=threshold_24h)

    sort_key = DISPUTE_SORT_FIELDS.get(selected_sort, "opened_at")
    order_prefix = "-" if selected_order != "asc" else ""
    disputes = disputes.order_by(f"{order_prefix}{sort_key}", "-id")

    return disputes, {
        "selected_tenant_id": selected_tenant_id,
        "selected_status": selected_status,
        "selected_reason": selected_reason,
        "selected_q": selected_q,
        "selected_opened_from": request.GET.get("opened_from", ""),
        "selected_opened_to": request.GET.get("opened_to", ""),
        "selected_sort": selected_sort if selected_sort in DISPUTE_SORT_FIELDS else "opened_at",
        "selected_order": selected_order if selected_order in {"asc", "desc"} else "desc",
        "selected_priority": selected_priority if selected_priority in DISPUTE_PRIORITY_CHOICES else "",
        "selected_module_id": selected_module_id,
        "auto_triage_sort_applied": auto_triage_sort_applied,
    }


def paginate_disputes(disputes, request, page_size=25):
    paginator = Paginator(disputes, page_size)
    page_obj = paginator.get_page(request.GET.get("page", 1))
    rows = list(page_obj.object_list)
    for row in rows:
        urgency_label, urgency_class = dispute_urgency_meta(row)
        row.urgency_label = urgency_label
        row.urgency_class = urgency_class
    page_query_params = request.GET.copy()
    if "page" in page_query_params:
        page_query_params.pop("page")
    return rows, page_obj, page_query_params.urlencode()
