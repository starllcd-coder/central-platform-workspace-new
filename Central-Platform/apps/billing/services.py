from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction
from django.db.models import Q, Sum
from django.utils import timezone

from apps.pricing.models import CommissionRule
from apps.tenants.models import TenantModule
from apps.tenants.policies import tenant_demo_block_reason

from .models import (
    LedgerEntry,
    PaymentTransaction,
    PayoutBatch,
    RefundRecord,
    Settlement,
    WalletAccount,
    WalletTransaction,
    WithdrawalRequest,
)

MONEY_Q = Decimal("0.001")


def _q(value):
    return Decimal(value).quantize(MONEY_Q, rounding=ROUND_HALF_UP)


def get_platform_wallet(currency="OMR"):
    wallet, _ = WalletAccount.objects.get_or_create(
        account_type="platform",
        tenant=None,
        defaults={"currency": currency, "status": "active"},
    )
    return wallet


def get_tenant_wallet(tenant, currency="OMR"):
    wallet, _ = WalletAccount.objects.get_or_create(
        account_type="tenant",
        tenant=tenant,
        defaults={"currency": currency or tenant.currency or "OMR", "status": "active"},
    )
    return wallet


def post_wallet_transaction(
    *,
    wallet: WalletAccount,
    tx_type: str,
    reason: str,
    amount,
    tenant=None,
    payment_transaction=None,
    settlement=None,
    notes="",
):
    amount_q = _q(amount)
    if amount_q <= 0:
        return None

    if tx_type == "credit":
        wallet.available_balance = _q(wallet.available_balance + amount_q)
    else:
        wallet.available_balance = _q(wallet.available_balance - amount_q)
        if wallet.available_balance < Decimal("0.00"):
            wallet.available_balance = Decimal("0.00")
    wallet.save(update_fields=["available_balance", "updated_at"])

    return WalletTransaction.objects.create(
        wallet=wallet,
        tenant=tenant,
        payment_transaction=payment_transaction,
        settlement=settlement,
        tx_type=tx_type,
        reason=reason,
        amount=amount_q,
        balance_after=wallet.available_balance,
        notes=notes,
    )


def resolve_commission_rate(tenant_id, module_id, booking_type, effective_date):
    base = CommissionRule.objects.filter(
        is_active=True,
        effective_from__lte=effective_date,
    ).filter(Q(effective_to__isnull=True) | Q(effective_to__gte=effective_date))

    candidates = base.filter(
        Q(tenant_id=tenant_id) | Q(tenant__isnull=True),
        Q(module_id=module_id) | Q(module__isnull=True),
        Q(booking_type=booking_type) | Q(booking_type="all"),
    )

    # Specificity order: tenant+module > tenant > module > global
    scored = []
    for item in candidates:
        score = 0
        if item.tenant_id == tenant_id:
            score += 2
        if item.module_id == module_id:
            score += 2
        if item.booking_type == booking_type:
            score += 1
        scored.append((score, item))
    if not scored:
        return Decimal("0.00")
    scored.sort(key=lambda x: (x[0], x[1].effective_from), reverse=True)
    return Decimal(scored[0][1].rate_percent)


def commission_applicable(tx: PaymentTransaction):
    if not tx.tenant.commission_enabled:
        return False

    if not tx.module_id:
        return True

    assignment = TenantModule.objects.filter(
        tenant_id=tx.tenant_id,
        module_id=tx.module_id,
        enabled=True,
    ).first()
    if assignment is None:
        return True
    if not assignment.marketplace_enabled:
        return False

    tx_date = tx.occurred_at.date()
    if assignment.commission_grace_until and tx_date <= assignment.commission_grace_until:
        return False
    return True


@transaction.atomic
def enrich_and_post_transaction(tx: PaymentTransaction):
    demo_issue = tenant_demo_block_reason(tx.tenant)
    if demo_issue:
        raise ValueError(demo_issue)

    commission_rate = Decimal("0.00")
    if commission_applicable(tx):
        commission_rate = resolve_commission_rate(
            tenant_id=tx.tenant_id,
            module_id=tx.module_id,
            booking_type=tx.booking_type or "online",
            effective_date=tx.occurred_at.date(),
        )
    gross = _q(tx.gross_amount or 0)
    gateway_fee = _q(tx.gateway_fee or 0)
    tax_amount = _q(tx.tax_amount or 0)
    commission_amount = _q((gross * commission_rate) / Decimal("100"))

    tx.commission_rate = commission_rate
    tx.commission_amount = commission_amount

    if tx.payment_channel == "online":
        tx.net_amount = _q(gross - commission_amount - gateway_fee - tax_amount)
        tx.business_due_for_cash = Decimal("0.00")
        tx.lifecycle_state = "posted"
    else:
        # Cash collected by business; platform creates receivable for commission.
        tx.net_amount = Decimal("0.00")
        tx.business_due_for_cash = commission_amount
        tx.settlement_state = "invoiced"
        tx.lifecycle_state = "review"

    tx.save(
        update_fields=[
            "commission_rate",
            "commission_amount",
            "net_amount",
            "business_due_for_cash",
            "lifecycle_state",
            "settlement_state",
        ]
    )

    LedgerEntry.objects.create(
        tenant=tx.tenant,
        transaction=tx,
        entry_type="payment_received",
        debit=gross if tx.payment_channel == "online" else Decimal("0.00"),
        credit=Decimal("0.00"),
        currency=tx.currency,
        notes=f"Booking {tx.booking_ref}",
    )
    LedgerEntry.objects.create(
        tenant=tx.tenant,
        transaction=tx,
        entry_type="commission_accrued",
        debit=Decimal("0.00"),
        credit=commission_amount,
        currency=tx.currency,
        notes=f"Commission for {tx.booking_ref}",
    )
    if gateway_fee > 0:
        LedgerEntry.objects.create(
            tenant=tx.tenant,
            transaction=tx,
            entry_type="gateway_fee",
            debit=Decimal("0.00"),
            credit=gateway_fee,
            currency=tx.currency,
            notes=f"Gateway fee for {tx.booking_ref}",
        )
    if tax_amount > 0:
        LedgerEntry.objects.create(
            tenant=tx.tenant,
            transaction=tx,
            entry_type="tax",
            debit=Decimal("0.00"),
            credit=tax_amount,
            currency=tx.currency,
            notes=f"Tax for {tx.booking_ref}",
        )
    if tx.payment_channel == "cash" and commission_amount > 0:
        LedgerEntry.objects.create(
            tenant=tx.tenant,
            transaction=tx,
            entry_type="cash_commission_receivable",
            debit=commission_amount,
            credit=Decimal("0.00"),
            currency=tx.currency,
            notes=f"Commission receivable on cash booking {tx.booking_ref}",
        )
    if tx.payment_channel == "online" and commission_amount > 0:
        platform_wallet = get_platform_wallet(currency=tx.currency)
        post_wallet_transaction(
            wallet=platform_wallet,
            tx_type="credit",
            reason="commission_accrual",
            amount=commission_amount,
            tenant=tx.tenant,
            payment_transaction=tx,
            notes=f"Commission accrued for {tx.booking_ref}",
        )


@transaction.atomic
def run_payout_batch(notes=""):
    batch = PayoutBatch.objects.create(
        code=f"PB-{timezone.now().strftime('%Y%m%d%H%M%S')}",
        status="processing",
        notes=notes,
    )

    txs = (
        PaymentTransaction.objects.select_related("tenant")
        .filter(
            payment_channel="online",
            status="paid",
            settlement_state="pending",
            tenant__account_type="production",
        )
        .order_by("tenant_id")
    )

    grouped = defaultdict(list)
    for tx in txs:
        grouped[tx.tenant_id].append(tx)

    for tenant_id, rows in grouped.items():
        gross = sum((r.gross_amount for r in rows), Decimal("0.00"))
        commission = sum((r.commission_amount for r in rows), Decimal("0.00"))
        net = sum((r.net_amount for r in rows), Decimal("0.00"))
        tenant = rows[0].tenant
        settlement = Settlement.objects.create(
            # Settlement represents payable amount to tenant wallet.
            tenant=tenant,
            payout_batch=batch,
            source_tx_count=len(rows),
            gross_amount=_q(gross),
            commission_amount=_q(commission),
            net_payout=_q(net),
            status="sent",
        )
        tenant_wallet = get_tenant_wallet(tenant=tenant, currency=rows[0].currency)
        post_wallet_transaction(
            wallet=tenant_wallet,
            tx_type="credit",
            reason="settlement_credit",
            amount=settlement.net_payout,
            tenant=tenant,
            settlement=settlement,
            notes=f"Settlement {batch.code}",
        )
        platform_wallet = get_platform_wallet(currency=rows[0].currency)
        post_wallet_transaction(
            wallet=platform_wallet,
            tx_type="debit",
            reason="settlement_credit",
            amount=settlement.net_payout,
            tenant=tenant,
            settlement=settlement,
            notes=f"Settlement paid {batch.code}",
        )
        LedgerEntry.objects.create(
            tenant=tenant,
            transaction=None,
            entry_type="payout_sent",
            debit=Decimal("0.00"),
            credit=_q(net),
            notes=f"Payout batch {batch.code}",
        )
        PaymentTransaction.objects.filter(id__in=[r.id for r in rows]).update(
            settlement_state="settled",
            lifecycle_state="settled",
        )

    batch.status = "sent"
    batch.processed_at = timezone.now()
    batch.save(update_fields=["status", "processed_at"])
    return batch


def outstanding_cash_commission_by_tenant(module_id=None):
    qs = PaymentTransaction.objects.filter(
            payment_channel="cash",
            status="paid",
            settlement_state="invoiced",
            tenant__account_type="production",
        )
    if module_id:
        qs = qs.filter(module_id=module_id)
    return qs.values("tenant_id", "tenant__name").annotate(amount=Sum("business_due_for_cash")).order_by(
        "-amount"
    )


@transaction.atomic
def process_refund(transaction_obj: PaymentTransaction, refund_type: str, refund_percent, reason: str):
    demo_issue = tenant_demo_block_reason(transaction_obj.tenant)
    if demo_issue:
        raise ValueError(demo_issue)

    if transaction_obj.status not in {"paid"}:
        raise ValueError("Only paid transactions can be refunded or cancelled.")

    percent = _q(refund_percent)
    if refund_type == "full":
        percent = Decimal("100.00")
    if percent <= 0 or percent > 100:
        raise ValueError("refund_percent must be > 0 and <= 100.")

    gross_refund = _q((transaction_obj.gross_amount * percent) / Decimal("100"))
    commission_reversal = _q((transaction_obj.commission_amount * percent) / Decimal("100"))
    business_recovery = Decimal("0.00")
    review_needed = False

    if transaction_obj.payment_channel == "online":
        # If payout already sent, this creates a receivable from business.
        if transaction_obj.settlement_state == "settled":
            business_recovery = _q((transaction_obj.net_amount * percent) / Decimal("100"))
            review_needed = True
            transaction_obj.settlement_state = "excluded"
            transaction_obj.lifecycle_state = "review"
        elif transaction_obj.settlement_state == "pending":
            transaction_obj.settlement_state = "excluded"
            transaction_obj.lifecycle_state = "refunded"
    else:
        # Cash refunds are handled by business, platform reverses commission receivable only.
        gross_refund = Decimal("0.00")
        transaction_obj.business_due_for_cash = _q(
            transaction_obj.business_due_for_cash - commission_reversal
        )
        if transaction_obj.business_due_for_cash < 0:
            transaction_obj.business_due_for_cash = Decimal("0.00")
        transaction_obj.lifecycle_state = "review" if transaction_obj.business_due_for_cash > 0 else "refunded"

    transaction_obj.refunded_amount = _q(transaction_obj.refunded_amount + gross_refund)
    if percent == Decimal("100.00"):
        transaction_obj.status = "refunded"
    else:
        transaction_obj.status = "refunded"
    if transaction_obj.status == "refunded" and transaction_obj.lifecycle_state != "review":
        transaction_obj.lifecycle_state = "refunded"
    transaction_obj.save(
        update_fields=[
            "status",
            "lifecycle_state",
            "settlement_state",
            "business_due_for_cash",
            "refunded_amount",
        ]
    )

    refund_record = RefundRecord.objects.create(
        transaction=transaction_obj,
        refund_type=refund_type,
        refund_percent=percent,
        customer_refund_amount=gross_refund,
        commission_reversal_amount=commission_reversal,
        business_recovery_amount=business_recovery,
        status="review" if review_needed else "processed",
        reason=reason or "",
    )

    if gross_refund > 0:
        LedgerEntry.objects.create(
            tenant=transaction_obj.tenant,
            transaction=transaction_obj,
            entry_type="refund",
            debit=Decimal("0.00"),
            credit=gross_refund,
            currency=transaction_obj.currency,
            notes=f"Refund for {transaction_obj.booking_ref}",
        )
    if commission_reversal > 0:
        LedgerEntry.objects.create(
            tenant=transaction_obj.tenant,
            transaction=transaction_obj,
            entry_type="commission_reversal",
            debit=commission_reversal,
            credit=Decimal("0.00"),
            currency=transaction_obj.currency,
            notes=f"Commission reversal for {transaction_obj.booking_ref}",
        )
        platform_wallet = get_platform_wallet(currency=transaction_obj.currency)
        post_wallet_transaction(
            wallet=platform_wallet,
            tx_type="debit",
            reason="adjustment",
            amount=commission_reversal,
            tenant=transaction_obj.tenant,
            payment_transaction=transaction_obj,
            notes=f"Commission reversal for {transaction_obj.booking_ref}",
        )
    if business_recovery > 0:
        LedgerEntry.objects.create(
            tenant=transaction_obj.tenant,
            transaction=transaction_obj,
            entry_type="refund_recovery_due",
            debit=business_recovery,
            credit=Decimal("0.00"),
            currency=transaction_obj.currency,
            notes=f"Recovery due from business for {transaction_obj.booking_ref}",
        )

    return refund_record


@transaction.atomic
def process_withdrawal_status_change(withdrawal: WithdrawalRequest, action: str, reviewed_by=None, notes=""):
    demo_issue = tenant_demo_block_reason(withdrawal.tenant)
    if demo_issue:
        raise ValueError(demo_issue)

    wallet = withdrawal.wallet
    amount = _q(withdrawal.amount)
    current = withdrawal.status

    if action == "approve":
        if current != "requested":
            raise ValueError("Only requested withdrawals can be approved.")
        if wallet.available_balance < amount:
            raise ValueError("Insufficient available wallet balance.")
        wallet.available_balance = _q(wallet.available_balance - amount)
        wallet.pending_balance = _q(wallet.pending_balance + amount)
        wallet.save(update_fields=["available_balance", "pending_balance", "updated_at"])
        withdrawal.status = "approved"
    elif action == "reject":
        if current not in {"requested", "approved"}:
            raise ValueError("Only requested/approved withdrawals can be rejected.")
        if current == "approved":
            wallet.available_balance = _q(wallet.available_balance + amount)
            wallet.pending_balance = _q(wallet.pending_balance - amount)
            if wallet.pending_balance < Decimal("0.00"):
                wallet.pending_balance = Decimal("0.00")
            wallet.save(update_fields=["available_balance", "pending_balance", "updated_at"])
        withdrawal.status = "rejected"
    elif action == "mark_paid":
        if current != "approved":
            raise ValueError("Only approved withdrawals can be marked paid.")
        wallet.pending_balance = _q(wallet.pending_balance - amount)
        if wallet.pending_balance < Decimal("0.00"):
            wallet.pending_balance = Decimal("0.00")
        wallet.save(update_fields=["pending_balance", "updated_at"])
        post_wallet_transaction(
            wallet=wallet,
            tx_type="debit",
            reason="withdrawal_debit",
            amount=amount,
            tenant=withdrawal.tenant,
            notes=f"Withdrawal paid WD-{withdrawal.id}",
        )
        withdrawal.status = "paid"
    else:
        raise ValueError("Unsupported withdrawal action.")

    withdrawal.reviewed_by = reviewed_by
    withdrawal.reviewed_at = timezone.now()
    if notes:
        withdrawal.notes = notes
    withdrawal.save(update_fields=["status", "reviewed_by", "reviewed_at", "notes"])
    return withdrawal
