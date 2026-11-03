import json
import csv
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.accounts.permissions import require_permission
from apps.accounts.services import (
    get_accessible_modules,
    get_user_tenant_ids,
    user_can_access_tenant,
    user_has_permission,
)
from apps.ops.services import log_audit, queue_notification
from apps.tenants.models import Module, Tenant
from apps.tenants.policies import (
    tenant_billing_block_reason,
    tenant_demo_block_reason,
    tenant_missing_required_policy,
)

from .forms import (
    CommissionInvoiceGenerateForm,
    DisputeCreateForm,
    DisputeResolveForm,
    PaymentTransactionForm,
    PayoutRunForm,
    RefundProcessForm,
    WithdrawalRequestActionForm,
    WithdrawalRequestCreateForm,
)
from .models import (
    CommissionInvoice,
    DisputeCase,
    PaymentTransaction,
    PayoutBatch,
    RefundRecord,
    Settlement,
    WalletAccount,
    WithdrawalRequest,
)
from .services import (
    enrich_and_post_transaction,
    outstanding_cash_commission_by_tenant,
    process_withdrawal_status_change,
    process_refund,
    run_payout_batch,
)
from .disputes_service import (
    apply_dispute_filters_and_sort,
    paginate_disputes,
)


def _active_module_id(request):
    active_module = getattr(request, "active_module", None)
    return active_module.id if active_module else None


def _has_billing_settle(user):
    return user_has_permission(user, "billing.settle")


def _billing_agreement_guard(request, tenant, *, api=False):
    missing = tenant_missing_required_policy(tenant, "billing")
    message_parts = []
    if missing:
        message_parts.append(
            "Required agreements are not accepted for this tenant: "
            + ", ".join(missing)
            + "."
        )
    pricing_block = tenant_billing_block_reason(tenant)
    if pricing_block:
        message_parts.append(pricing_block)

    if not message_parts:
        return None
    message = " ".join(message_parts)
    if api:
        return JsonResponse({"detail": message, "missing_agreements": missing}, status=409)
    messages.error(request, message)
    return redirect("tenant-agreements")


def _demo_tenant_guard(request, tenant, *, api=False):
    issue = tenant_demo_block_reason(tenant)
    if not issue:
        return None
    if api:
        return JsonResponse({"detail": issue}, status=409)
    messages.error(request, issue)
    return redirect("billing-list")


def _tx_payload(tx, *, duplicate=False):
    return {
        "id": tx.id,
        "tenant_id": tx.tenant_id,
        "booking_ref": tx.booking_ref,
        "commission_amount": str(tx.commission_amount),
        "net_amount": str(tx.net_amount),
        "cash_commission_due": str(tx.business_due_for_cash),
        "settlement_state": tx.settlement_state,
        "lifecycle_state": tx.lifecycle_state,
        "idempotency_key": tx.idempotency_key,
        "external_payment_ref": tx.external_payment_ref,
        "gateway_txn_ref": tx.gateway_txn_ref,
        "duplicate": duplicate,
    }


@login_required
def billing_list(request):
    tenant_ids = get_user_tenant_ids(request.user) if not request.user.is_superuser else None
    active_tenant = getattr(request, "active_tenant", None)
    active_module_id = _active_module_id(request)

    settlements = Settlement.objects.select_related("tenant", "payout_batch")
    transactions = PaymentTransaction.objects.select_related("tenant", "module")
    invoices = CommissionInvoice.objects.select_related("tenant")
    refunds = RefundRecord.objects.select_related("transaction", "transaction__tenant")
    disputes = DisputeCase.objects.select_related("tenant", "transaction")
    wallets = WalletAccount.objects.select_related("tenant")
    withdrawals = WithdrawalRequest.objects.select_related("tenant", "wallet", "requested_by", "reviewed_by")
    batches = PayoutBatch.objects.all()[:10]

    if tenant_ids is not None:
        settlements = settlements.filter(tenant_id__in=tenant_ids)
        transactions = transactions.filter(tenant_id__in=tenant_ids)
        invoices = invoices.filter(tenant_id__in=tenant_ids)
        refunds = refunds.filter(transaction__tenant_id__in=tenant_ids)
        disputes = disputes.filter(tenant_id__in=tenant_ids)
        wallets = wallets.filter(
            models.Q(account_type="platform") | models.Q(tenant_id__in=tenant_ids)
        )
        withdrawals = withdrawals.filter(tenant_id__in=tenant_ids)
    if active_tenant:
        settlements = settlements.filter(tenant=active_tenant)
        transactions = transactions.filter(tenant=active_tenant)
        invoices = invoices.filter(tenant=active_tenant)
        refunds = refunds.filter(transaction__tenant=active_tenant)
        disputes = disputes.filter(tenant=active_tenant)
        wallets = wallets.filter(models.Q(account_type="platform") | models.Q(tenant=active_tenant))
        withdrawals = withdrawals.filter(tenant=active_tenant)
    if active_module_id:
        transactions = transactions.filter(module_id=active_module_id)
        refunds = refunds.filter(transaction__module_id=active_module_id)
        disputes = disputes.filter(transaction__module_id=active_module_id)

    settlements = settlements[:20]
    transactions = transactions[:20]
    invoices = invoices[:20]
    refunds = refunds[:20]
    disputes = disputes[:10]
    wallets = wallets.order_by("account_type", "tenant__name")[:20]
    withdrawals = withdrawals[:20]

    totals_qs = PaymentTransaction.objects.filter(status="paid")
    if tenant_ids is not None:
        totals_qs = totals_qs.filter(tenant_id__in=tenant_ids)
    if active_tenant:
        totals_qs = totals_qs.filter(tenant=active_tenant)
    if active_module_id:
        totals_qs = totals_qs.filter(module_id=active_module_id)
    totals = totals_qs.aggregate(
        gross=Sum("gross_amount"),
        commission=Sum("commission_amount"),
        net=Sum("net_amount"),
        cash_due=Sum("business_due_for_cash"),
    )

    tx_form = PaymentTransactionForm()
    payout_form = PayoutRunForm()
    withdrawal_create_form = WithdrawalRequestCreateForm()
    withdrawal_action_form = WithdrawalRequestActionForm()
    tenant_qs = Tenant.objects.all().order_by("name")
    if tenant_ids is not None:
        tenant_qs = tenant_qs.filter(id__in=tenant_ids)
    if active_tenant:
        tenant_qs = tenant_qs.filter(id=active_tenant.id)
    invoice_form = CommissionInvoiceGenerateForm(tenant_queryset=tenant_qs)

    cash_outstanding = outstanding_cash_commission_by_tenant(module_id=active_module_id)
    if tenant_ids is not None:
        allowed = set(tenant_ids)
        cash_outstanding = [row for row in cash_outstanding if row["tenant_id"] in allowed]
    if active_tenant:
        cash_outstanding = [row for row in cash_outstanding if row["tenant_id"] == active_tenant.id]

    module_qs = get_accessible_modules(request.user, tenant=active_tenant)
    tx_form.fields["module"].queryset = module_qs
    if active_module_id:
        tx_form.fields["module"].initial = active_module_id
    if active_tenant:
        tx_form.fields["tenant"].initial = active_tenant.id
        tx_form.fields["tenant"].queryset = tenant_qs
        tenant_wallet = WalletAccount.objects.filter(account_type="tenant", tenant=active_tenant).first()
        if tenant_wallet:
            withdrawal_create_form.initial["amount"] = "0.00"
    else:
        tenant_wallet = None

    return render(
        request,
        "billing/list.html",
        {
            "settlements": settlements,
            "transactions": transactions,
            "batches": batches,
            "invoices": invoices,
            "totals": totals,
            "tx_form": tx_form,
            "payout_form": payout_form,
            "invoice_form": invoice_form,
            "cash_outstanding": cash_outstanding,
            "refunds": refunds,
            "disputes": disputes,
            "wallets": wallets,
            "withdrawals": withdrawals,
            "withdrawal_create_form": withdrawal_create_form,
            "withdrawal_action_form": withdrawal_action_form,
            "active_tenant_wallet": tenant_wallet,
        },
    )


@login_required
@require_http_methods(["POST"])
@require_permission("billing.settle")
def transaction_create(request):
    form = PaymentTransactionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Could not create transaction. Check form fields.")
        return redirect("billing-list")

    tx = form.save(commit=False)
    active_module_id = _active_module_id(request)
    if active_module_id and tx.module_id != active_module_id:
        messages.error(request, "Selected module context does not match transaction module.")
        return redirect("billing-list")
    if not user_can_access_tenant(request.user, tx.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, tx.tenant, api=False)
    if blocked:
        return blocked
    blocked = _billing_agreement_guard(request, tx.tenant, api=False)
    if blocked:
        return blocked

    tx.status = "paid"
    tx.settlement_state = "pending"
    tx.save()
    enrich_and_post_transaction(tx)

    log_audit(
        actor=request.user,
        tenant=tx.tenant,
        module=tx.module,
        action="billing.transaction.created",
        entity_type="PaymentTransaction",
        entity_id=tx.id,
        metadata={"booking_ref": tx.booking_ref, "channel": tx.payment_channel},
    )
    queue_notification(
        channel="in_app",
        recipient=tx.tenant.owner_email or "",
        tenant=tx.tenant,
        module=tx.module,
        triggered_by=request.user,
        subject="New payment transaction posted",
        body=f"Booking {tx.booking_ref} posted with gross {tx.gross_amount} {tx.currency}.",
        context={"booking_ref": tx.booking_ref},
    )
    messages.success(request, "Payment transaction posted and ledger entries created.")
    return redirect("billing-list")


@login_required
@require_http_methods(["POST"])
@require_permission("billing.settle")
def payout_run(request):
    form = PayoutRunForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Payout form is invalid.")
        return redirect("billing-list")

    batch = run_payout_batch(notes=form.cleaned_data.get("notes", ""))
    log_audit(
        actor=request.user,
        action="billing.payout.batch.run",
        entity_type="PayoutBatch",
        entity_id=batch.id,
        metadata={"code": batch.code, "status": batch.status},
    )
    queue_notification(
        channel="in_app",
        recipient="ops",
        triggered_by=request.user,
        subject="Payout batch completed",
        body=f"Payout batch {batch.code} completed with status {batch.status}.",
    )
    messages.success(request, f"Payout batch {batch.code} generated.")
    return redirect("billing-list")


@login_required
@require_http_methods(["POST"])
@require_permission("commission.manage")
def generate_cash_commission_invoice(request):
    tenant_qs = Tenant.objects.all().order_by("name")
    if not request.user.is_superuser:
        tenant_qs = tenant_qs.filter(id__in=get_user_tenant_ids(request.user))
    form = CommissionInvoiceGenerateForm(request.POST, tenant_queryset=tenant_qs)
    if not form.is_valid():
        messages.error(request, "Invoice form is invalid.")
        return redirect("billing-list")

    tenant = form.cleaned_data["tenant"]
    if not user_can_access_tenant(request.user, tenant.id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, tenant, api=False)
    if blocked:
        return blocked

    due_date = form.cleaned_data["due_date"]
    notes = form.cleaned_data.get("notes", "")
    amount = (
        PaymentTransaction.objects.filter(
            tenant=tenant,
            payment_channel="cash",
            status="paid",
            settlement_state="invoiced",
        ).aggregate(total=Sum("business_due_for_cash"))["total"]
        or Decimal("0.00")
    )
    if amount <= 0:
        messages.warning(request, "No pending cash commission found for selected tenant.")
        return redirect("billing-list")

    code = f"CINV-{tenant.tenant_code}-{CommissionInvoice.objects.count() + 1:04d}"
    CommissionInvoice.objects.create(
        tenant=tenant,
        code=code,
        amount_due=amount,
        due_date=due_date,
        notes=notes,
        status="pending",
    )
    PaymentTransaction.objects.filter(
        tenant=tenant,
        payment_channel="cash",
        status="paid",
        settlement_state="invoiced",
    ).update(settlement_state="excluded")
    log_audit(
        actor=request.user,
        tenant=tenant,
        action="billing.cash.invoice.generated",
        entity_type="CommissionInvoice",
        entity_id=code,
        metadata={"amount_due": str(amount), "due_date": due_date.isoformat()},
    )
    queue_notification(
        channel="in_app",
        recipient=tenant.owner_email or "",
        tenant=tenant,
        triggered_by=request.user,
        subject="Cash commission invoice generated",
        body=f"Invoice {code} generated for {amount} {tenant.currency}.",
    )
    messages.success(request, f"Commission invoice {code} created.")
    return redirect("billing-list")


@login_required
@require_http_methods(["POST"])
@require_permission("billing.settle")
def withdrawal_request_create(request):
    active_tenant = getattr(request, "active_tenant", None)
    if not active_tenant:
        messages.error(request, "Select an active tenant before creating a withdrawal.")
        return redirect("billing-list")
    if not user_can_access_tenant(request.user, active_tenant.id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, active_tenant, api=False)
    if blocked:
        return blocked

    wallet = WalletAccount.objects.filter(account_type="tenant", tenant=active_tenant).first()
    if wallet is None:
        messages.error(request, "Tenant wallet not found. Run a payout batch first.")
        return redirect("billing-list")

    form = WithdrawalRequestCreateForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Withdrawal request form is invalid.")
        return redirect("billing-list")

    amount = form.cleaned_data["amount"]
    if wallet.available_balance < amount:
        messages.error(request, "Insufficient wallet available balance for this withdrawal.")
        return redirect("billing-list")

    wd = WithdrawalRequest.objects.create(
        tenant=active_tenant,
        wallet=wallet,
        amount=amount,
        currency=wallet.currency,
        status="requested",
        notes=form.cleaned_data.get("notes", ""),
        requested_by=request.user,
    )
    log_audit(
        actor=request.user,
        tenant=active_tenant,
        action="billing.withdrawal.requested",
        entity_type="WithdrawalRequest",
        entity_id=wd.id,
        metadata={"amount": str(wd.amount), "currency": wd.currency},
    )
    queue_notification(
        channel="in_app",
        recipient="ops",
        tenant=active_tenant,
        triggered_by=request.user,
        subject="Withdrawal request created",
        body=f"Withdrawal WD-{wd.id} requested for {wd.amount} {wd.currency}.",
    )
    messages.success(request, f"Withdrawal request WD-{wd.id} created.")
    return redirect("billing-list")


@login_required
@require_http_methods(["POST"])
@require_permission("billing.settle")
def withdrawal_request_update(request, withdrawal_id):
    wd = WithdrawalRequest.objects.select_related("tenant", "wallet").filter(pk=withdrawal_id).first()
    if wd is None:
        return JsonResponse({"detail": "Withdrawal request not found."}, status=404)
    if not user_can_access_tenant(request.user, wd.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, wd.tenant, api=False)
    if blocked:
        return blocked

    form = WithdrawalRequestActionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Withdrawal action form is invalid.")
        return redirect("billing-list")

    action = form.cleaned_data["action"]
    try:
        process_withdrawal_status_change(
            withdrawal=wd,
            action=action,
            reviewed_by=request.user,
            notes=form.cleaned_data.get("notes", ""),
        )
    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("billing-list")

    log_audit(
        actor=request.user,
        tenant=wd.tenant,
        action="billing.withdrawal.updated",
        entity_type="WithdrawalRequest",
        entity_id=wd.id,
        metadata={"status": wd.status, "action": action},
    )
    queue_notification(
        channel="in_app",
        recipient=wd.tenant.owner_email or "",
        tenant=wd.tenant,
        triggered_by=request.user,
        subject="Withdrawal request updated",
        body=f"Withdrawal WD-{wd.id} moved to {wd.get_status_display()}.",
    )
    messages.success(request, f"Withdrawal WD-{wd.id} updated to {wd.get_status_display()}.")
    return redirect("billing-list")


@csrf_exempt
@require_http_methods(["POST"])
def transaction_create_api(request):
    if not _has_billing_settle(request.user):
        return JsonResponse({"detail": "Permission denied."}, status=403)
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    form = PaymentTransactionForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)

    tx = form.save(commit=False)
    idempotency_key = (
        str(payload.get("idempotency_key", "")).strip()
        or request.headers.get("X-Idempotency-Key", "").strip()
    )
    external_payment_ref = str(payload.get("external_payment_ref", "")).strip()
    gateway_txn_ref = str(payload.get("gateway_txn_ref", "")).strip()

    if idempotency_key:
        existing = (
            PaymentTransaction.objects.filter(
                tenant_id=tx.tenant_id,
                module_id=tx.module_id,
                idempotency_key=idempotency_key,
            )
            .order_by("-id")
            .first()
        )
        if existing:
            return JsonResponse(_tx_payload(existing, duplicate=True), status=200)

    active_module_id = _active_module_id(request)
    if active_module_id and tx.module_id != active_module_id:
        return JsonResponse({"detail": "Module context mismatch."}, status=409)
    if not user_can_access_tenant(request.user, tx.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, tx.tenant, api=True)
    if blocked:
        return blocked
    blocked = _billing_agreement_guard(request, tx.tenant, api=True)
    if blocked:
        return blocked
    tx.status = "paid"
    tx.settlement_state = "pending"
    tx.idempotency_key = idempotency_key
    tx.external_payment_ref = external_payment_ref
    tx.gateway_txn_ref = gateway_txn_ref
    tx.save()
    enrich_and_post_transaction(tx)
    return JsonResponse(_tx_payload(tx), status=201)


@login_required
@require_permission("billing.settle")
def refund_process_page(request, tx_id):
    tx = PaymentTransaction.objects.select_related("tenant", "module").filter(pk=tx_id).first()
    if tx is None:
        return JsonResponse({"detail": "Transaction not found."}, status=404)
    if not user_can_access_tenant(request.user, tx.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, tx.tenant, api=False)
    if blocked:
        return blocked

    if request.method == "POST":
        form = RefundProcessForm(request.POST)
        if form.is_valid():
            try:
                record = process_refund(
                    transaction_obj=tx,
                    refund_type=form.cleaned_data["refund_type"],
                    refund_percent=form.cleaned_data["refund_percent"],
                    reason=form.cleaned_data.get("reason", ""),
                )
                log_audit(
                    actor=request.user,
                    tenant=tx.tenant,
                    module=tx.module,
                    action="billing.refund.processed",
                    entity_type="RefundRecord",
                    entity_id=record.id,
                    metadata={
                        "booking_ref": tx.booking_ref,
                        "refund_type": record.refund_type,
                        "refund_percent": str(record.refund_percent),
                        "customer_refund_amount": str(record.customer_refund_amount),
                    },
                )
                queue_notification(
                    channel="in_app",
                    recipient=tx.tenant.owner_email or "",
                    tenant=tx.tenant,
                    module=tx.module,
                    triggered_by=request.user,
                    subject="Refund processed",
                    body=f"Refund processed for booking {tx.booking_ref}: {record.customer_refund_amount} {tx.currency}.",
                )
                messages.success(request, f"Refund processed (record #{record.id}).")
                return redirect("billing-list")
            except ValueError as exc:
                messages.error(request, str(exc))
    else:
        form = RefundProcessForm()

    return render(request, "billing/refund_form.html", {"tx": tx, "form": form})


@csrf_exempt
@require_http_methods(["POST"])
def transaction_refund_api(request, tx_id):
    if not user_has_permission(request.user, "billing.settle"):
        return JsonResponse({"detail": "Permission denied."}, status=403)

    tx = PaymentTransaction.objects.filter(pk=tx_id).first()
    if tx is None:
        return JsonResponse({"detail": "Transaction not found."}, status=404)
    if not user_can_access_tenant(request.user, tx.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, tx.tenant, api=True)
    if blocked:
        return blocked

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    try:
        record = process_refund(
            transaction_obj=tx,
            refund_type=payload.get("refund_type", "full"),
            refund_percent=payload.get("refund_percent", "100"),
            reason=payload.get("reason", ""),
        )
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    return JsonResponse(
        {
            "refund_record_id": record.id,
            "transaction_id": tx.id,
            "transaction_status": tx.status,
            "refund_amount": str(record.customer_refund_amount),
            "commission_reversal_amount": str(record.commission_reversal_amount),
            "business_recovery_amount": str(record.business_recovery_amount),
            "refund_status": record.status,
        },
        status=201,
    )


@login_required
def dispute_list(request):
    if not (user_has_permission(request.user, "reports.view") or _has_billing_settle(request.user)):
        return JsonResponse({"detail": "Permission denied."}, status=403)

    disputes = DisputeCase.objects.select_related("tenant", "transaction")
    tenant_qs = Tenant.objects.all().order_by("name")
    tx_qs = PaymentTransaction.objects.select_related("tenant").order_by("-occurred_at")
    active_tenant = getattr(request, "active_tenant", None)
    active_module_id = _active_module_id(request)
    if not request.user.is_superuser:
        tenant_ids = get_user_tenant_ids(request.user)
        disputes = disputes.filter(tenant_id__in=tenant_ids)
        tenant_qs = tenant_qs.filter(id__in=tenant_ids)
        tx_qs = tx_qs.filter(tenant_id__in=tenant_ids)
    if active_tenant:
        disputes = disputes.filter(tenant=active_tenant)
        tenant_qs = tenant_qs.filter(id=active_tenant.id)
        tx_qs = tx_qs.filter(tenant=active_tenant)
    if active_module_id:
        tx_qs = tx_qs.filter(module_id=active_module_id)

    disputes, filter_state = apply_dispute_filters_and_sort(disputes, request, active_module_id)
    dispute_rows, page_obj, page_query = paginate_disputes(disputes, request, page_size=25)

    create_form = DisputeCreateForm()
    create_form.fields["tenant"].queryset = tenant_qs
    create_form.fields["transaction"].queryset = tx_qs[:300]

    resolve_form = DisputeResolveForm()
    return render(
        request,
        "billing/disputes.html",
        {
            "disputes": dispute_rows,
            "page_obj": page_obj,
            "create_form": create_form,
            "resolve_form": resolve_form,
            "tenant_options": tenant_qs[:200],
            "status_options": DisputeCase.STATUS_CHOICES,
            "reason_options": DisputeCase.REASON_CHOICES,
            "sort_options": [
                ("opened_at", "Opened Date"),
                ("status", "Status"),
                ("tenant", "Tenant"),
                ("code", "Code"),
            ],
            "priority_options": [
                ("", "Any Priority"),
                ("high", "High Priority"),
                ("attention", "Attention"),
                ("normal", "Normal"),
            ],
            **filter_state,
            "page_query": page_query,
        },
    )


@login_required
@require_http_methods(["GET"])
def dispute_export_csv(request):
    if not (user_has_permission(request.user, "reports.view") or _has_billing_settle(request.user)):
        return JsonResponse({"detail": "Permission denied."}, status=403)

    disputes = DisputeCase.objects.select_related("tenant", "transaction", "created_by", "resolved_by")
    active_tenant = getattr(request, "active_tenant", None)
    if not request.user.is_superuser:
        disputes = disputes.filter(tenant_id__in=get_user_tenant_ids(request.user))
    if active_tenant:
        disputes = disputes.filter(tenant=active_tenant)
    disputes, _ = apply_dispute_filters_and_sort(
        disputes,
        request,
        _active_module_id(request),
    )

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="disputes_export.csv"'
    writer = csv.writer(response)
    writer.writerow(
        [
            "id",
            "code",
            "tenant_id",
            "tenant_name",
            "transaction_id",
            "booking_ref",
            "reason",
            "description",
            "status",
            "resolution_type",
            "resolution_notes",
            "opened_at",
            "resolved_at",
            "created_by",
            "resolved_by",
        ]
    )
    for dispute in disputes[:1000]:
        writer.writerow(
            [
                dispute.id,
                dispute.code,
                dispute.tenant_id,
                dispute.tenant.name if dispute.tenant else "",
                dispute.transaction_id or "",
                dispute.transaction.booking_ref if dispute.transaction else "",
                dispute.reason,
                dispute.description,
                dispute.status,
                dispute.resolution_type,
                dispute.resolution_notes,
                dispute.opened_at.isoformat() if dispute.opened_at else "",
                dispute.resolved_at.isoformat() if dispute.resolved_at else "",
                dispute.created_by.username if dispute.created_by else "",
                dispute.resolved_by.username if dispute.resolved_by else "",
            ]
        )
    return response


@login_required
@require_http_methods(["POST"])
@require_permission("billing.settle")
def dispute_create(request):
    form = DisputeCreateForm(request.POST)
    tenant_qs = Tenant.objects.all().order_by("name")
    tx_qs = PaymentTransaction.objects.select_related("tenant").order_by("-occurred_at")
    if not request.user.is_superuser:
        tenant_ids = get_user_tenant_ids(request.user)
        tenant_qs = tenant_qs.filter(id__in=tenant_ids)
        tx_qs = tx_qs.filter(tenant_id__in=tenant_ids)
    form.fields["tenant"].queryset = tenant_qs
    form.fields["transaction"].queryset = tx_qs[:300]

    if not form.is_valid():
        messages.error(request, "Dispute form is invalid.")
        return redirect("billing-disputes")

    dispute = form.save(commit=False)
    active_module_id = _active_module_id(request)
    if active_module_id and dispute.transaction and dispute.transaction.module_id != active_module_id:
        messages.error(request, "Selected module context does not match dispute transaction module.")
        return redirect("billing-disputes")
    if not user_can_access_tenant(request.user, dispute.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, dispute.tenant, api=False)
    if blocked:
        return blocked
    dispute.code = f"DSP-{dispute.tenant.tenant_code}-{DisputeCase.objects.count() + 1:05d}"
    dispute.created_by = request.user
    dispute.save()

    log_audit(
        actor=request.user,
        tenant=dispute.tenant,
        module=dispute.transaction.module if dispute.transaction else None,
        action="billing.dispute.created",
        entity_type="DisputeCase",
        entity_id=dispute.id,
        metadata={"code": dispute.code, "reason": dispute.reason},
    )
    queue_notification(
        channel="in_app",
        recipient=dispute.tenant.owner_email or "",
        tenant=dispute.tenant,
        triggered_by=request.user,
        subject="Dispute case opened",
        body=f"Dispute {dispute.code} has been opened for review.",
    )
    messages.success(request, f"Dispute {dispute.code} created.")
    return redirect("billing-disputes")


@login_required
@require_http_methods(["POST"])
@require_permission("billing.settle")
def dispute_update(request, dispute_id):
    dispute = DisputeCase.objects.select_related("tenant", "transaction").filter(pk=dispute_id).first()
    if dispute is None:
        return JsonResponse({"detail": "Dispute not found."}, status=404)
    if not user_can_access_tenant(request.user, dispute.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, dispute.tenant, api=False)
    if blocked:
        return blocked

    form = DisputeResolveForm(request.POST, instance=dispute)
    if not form.is_valid():
        messages.error(request, "Dispute update form is invalid.")
        return redirect("billing-disputes")

    dispute = form.save(commit=False)
    if dispute.status in {"resolved", "rejected"}:
        from django.utils import timezone

        dispute.resolved_at = timezone.now()
        dispute.resolved_by = request.user
    dispute.save()

    log_audit(
        actor=request.user,
        tenant=dispute.tenant,
        module=dispute.transaction.module if dispute.transaction else None,
        action="billing.dispute.updated",
        entity_type="DisputeCase",
        entity_id=dispute.id,
        metadata={"status": dispute.status, "resolution_type": dispute.resolution_type},
    )
    queue_notification(
        channel="in_app",
        recipient=dispute.tenant.owner_email or "",
        tenant=dispute.tenant,
        triggered_by=request.user,
        subject="Dispute case updated",
        body=f"Dispute {dispute.code} moved to status {dispute.get_status_display()}.",
    )
    messages.success(request, f"Dispute {dispute.code} updated.")
    return redirect("billing-disputes")


@csrf_exempt
@require_http_methods(["POST"])
def dispute_create_api(request):
    if not _has_billing_settle(request.user):
        return JsonResponse({"detail": "Permission denied."}, status=403)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    form = DisputeCreateForm(payload)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)
    dispute = form.save(commit=False)
    active_module_id = _active_module_id(request)
    if active_module_id and dispute.transaction and dispute.transaction.module_id != active_module_id:
        return JsonResponse({"detail": "Module context mismatch."}, status=409)
    if not user_can_access_tenant(request.user, dispute.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, dispute.tenant, api=True)
    if blocked:
        return blocked
    dispute.code = f"DSP-{dispute.tenant.tenant_code}-{DisputeCase.objects.count() + 1:05d}"
    dispute.created_by = request.user
    dispute.save()
    return JsonResponse(
        {
            "id": dispute.id,
            "code": dispute.code,
            "status": dispute.status,
            "tenant_id": dispute.tenant_id,
            "transaction_id": dispute.transaction_id,
        },
        status=201,
    )


@csrf_exempt
@require_http_methods(["POST"])
def dispute_update_api(request, dispute_id):
    if not _has_billing_settle(request.user):
        return JsonResponse({"detail": "Permission denied."}, status=403)
    dispute = DisputeCase.objects.filter(pk=dispute_id).first()
    if dispute is None:
        return JsonResponse({"detail": "Dispute not found."}, status=404)
    if not user_can_access_tenant(request.user, dispute.tenant_id):
        return JsonResponse({"detail": "Tenant access denied."}, status=403)
    blocked = _demo_tenant_guard(request, dispute.tenant, api=True)
    if blocked:
        return blocked
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return HttpResponseBadRequest("Invalid JSON payload")

    form = DisputeResolveForm(payload, instance=dispute)
    if not form.is_valid():
        return JsonResponse({"errors": form.errors}, status=400)
    dispute = form.save(commit=False)
    if dispute.status in {"resolved", "rejected"}:
        from django.utils import timezone

        dispute.resolved_at = timezone.now()
        dispute.resolved_by = request.user
    dispute.save()
    return JsonResponse(
        {
            "id": dispute.id,
            "code": dispute.code,
            "status": dispute.status,
            "resolution_type": dispute.resolution_type,
        }
    )
