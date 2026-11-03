from __future__ import annotations

import hashlib
import hmac
import json
from decimal import Decimal
from datetime import datetime, timezone as dt_timezone
from uuid import uuid4

from django.conf import settings
from django.db import IntegrityError
from django.db import models
from django.db import transaction
from django.utils import timezone

from apps.billing.models import PaymentTransaction
from apps.billing.services import enrich_and_post_transaction
from apps.pricing.models import CommissionRule
from apps.tenants.models import Tenant
from apps.tenants.policies import tenant_demo_block_reason

from .adapters import StripeAdapter, TapAdapter, ThawaniAdapter
from .models import (
    CentralPayment,
    CentralRefund,
    GatewayConfig,
    GatewayProvider,
    PaymentStatus,
    PaymentWebhookLog,
    RoutingRule,
)


def _csv_tokens(value: str) -> set[str]:
    return {item.strip().lower() for item in (value or "").split(",") if item.strip()}


def _supports(config, currency):
    if getattr(settings,"PAYMENT_GATEWAY_MODE","mock")!="live": return True
    if config.provider not in {GatewayProvider.STRIPE,GatewayProvider.THAWANI}:return False
    supported=config.settings_json.get("currencies") or (["OMR"] if config.provider==GatewayProvider.THAWANI else ["USD","AED","SAR","EUR","GBP"])
    return currency.upper() in supported


def select_gateway(*, country_code: str, currency: str, module_code: str, payment_method: str) -> str:
    country = (country_code or "").strip().lower()
    ccy = (currency or "").strip().lower()
    module = (module_code or "").strip().lower()
    method = (payment_method or "").strip().lower()

    rules = RoutingRule.objects.filter(is_enabled=True).order_by("priority", "id")
    for rule in rules:
        countries = _csv_tokens(rule.countries_csv)
        currencies = _csv_tokens(rule.currencies_csv)
        modules = _csv_tokens(rule.module_codes_csv)
        methods = _csv_tokens(rule.payment_methods_csv)

        if countries and country not in countries:
            continue
        if currencies and ccy not in currencies:
            continue
        if modules and module not in modules:
            continue
        if methods and method not in methods:
            continue
        cfg = GatewayConfig.objects.filter(provider=rule.gateway, is_enabled=True).first()
        if cfg and _supports(cfg,currency):
            return rule.gateway

    for enabled in GatewayConfig.objects.filter(is_enabled=True).order_by("priority", "provider"):
        if _supports(enabled,currency): return enabled.provider
    if getattr(settings,"PAYMENT_GATEWAY_MODE","mock")=="live":raise ValueError("No configured gateway supports this booking currency.")
    return GatewayProvider.STRIPE



def build_adapter(provider: str):
    gateway_mode = getattr(settings, "PAYMENT_GATEWAY_MODE", "mock")
    if gateway_mode == "disabled":
        raise ValueError("Payment gateways are disabled.")
    if gateway_mode == "live":
        from .live_adapters import StripeLiveAdapter, ThawaniLiveAdapter
        config = GatewayConfig.objects.filter(provider=provider,is_enabled=True).first()
        if not config: raise ValueError("Gateway is not enabled.")
        if provider == GatewayProvider.STRIPE: return StripeLiveAdapter(config)
        if provider == GatewayProvider.THAWANI: return ThawaniLiveAdapter(config)
        raise ValueError("Only Thawani and Stripe are enabled for live checkout.")
    if gateway_mode != "mock":
        raise ValueError("Unsupported gateway mode.")
    if provider == GatewayProvider.THAWANI:
        return ThawaniAdapter()
    if provider == GatewayProvider.TAP:
        return TapAdapter()
    return StripeAdapter()


def _commission_amount(tenant, module, booking_type: str, amount: Decimal):
    base = CommissionRule.objects.filter(is_active=True).filter(
        tenant__in=[tenant, None],
        module__in=[module, None],
        booking_type__in=[booking_type, "all"],
    ).order_by("-effective_from", "-id")
    rate = Decimal("0.00")
    if base.exists():
        rate = Decimal(base.first().rate_percent or 0)
    commission = (amount * rate / Decimal("100")).quantize(Decimal("0.001"))
    return rate, commission


@transaction.atomic
def create_payment(payload: dict):
    tenant = Tenant.objects.get(pk=payload["tenant_id"])
    demo_issue = tenant_demo_block_reason(tenant)
    if demo_issue:
        raise ValueError(demo_issue)
    module = tenant.tenant_modules.filter(enabled=True, module__code=payload.get("module_code", "")).select_related("module").first()
    module_obj = module.module if module else None
    amount = Decimal(str(payload["amount"]))
    if not amount.is_finite() or amount <= 0:
        raise ValueError("amount must be a positive finite value.")
    currency = str(payload.get("currency") or tenant.currency or "OMR")
    payment_method = str(payload.get("payment_method") or "card")
    booking_type = str(payload.get("booking_type") or "online")
    idempotency_key = str(payload.get("idempotency_key") or "").strip()

    if idempotency_key:
        existing = CentralPayment.objects.filter(
            tenant=tenant,
            idempotency_key=idempotency_key,
        ).order_by("-id").first()
        if existing:
            return existing, True

    provider = select_gateway(
        country_code=str(payload.get("country_code") or "").strip(),
        currency=currency,
        module_code=str(payload.get("module_code") or "").strip(),
        payment_method=payment_method,
    )
    adapter = build_adapter(provider)
    payment_id = "pay_" + (hashlib.sha256(f"{tenant.pk}:{idempotency_key}".encode()).hexdigest()[:24] if idempotency_key else uuid4().hex[:24])
    commission_rate, commission_amount = _commission_amount(tenant, module_obj, booking_type, amount)
    business_share = (amount - commission_amount).quantize(Decimal("0.001"))

    try:
        with transaction.atomic():
            payment = CentralPayment.objects.create(
                payment_id=payment_id,
                idempotency_key=idempotency_key,
                tenant=tenant,
                module=module_obj,
                booking_id=str(payload.get("booking_id") or ""),
                parent_booking_id=str(payload.get("parent_booking_id") or ""),
                customer_id=str(payload.get("customer_id") or ""),
                business_id=str(payload.get("business_id") or tenant.tenant_code),
                gateway_name=provider,
                payment_method=payment_method,
                amount=amount,
                currency=currency,
                country_code=str(payload.get("country_code") or ""),
                transaction_status=PaymentStatus.PENDING,
                refund_status="none",
                commission_amount=commission_amount,
                business_share=business_share,
                is_card_guarantee=bool(payload.get("is_card_guarantee", False)),
                is_extension_payment=bool(payload.get("is_extension_payment", False)),
                metadata={"commission_rate": str(commission_rate), **(payload.get("metadata") or {}), "card_guarantee": bool(payload.get("is_card_guarantee", False))},
            )
    except IntegrityError:
        if idempotency_key:
            existing = CentralPayment.objects.filter(
                tenant=tenant, idempotency_key=idempotency_key
            ).first()
            if existing:
                return existing, True
        raise
    session = adapter.create_payment_session(
        payment_id=payment.payment_id,
        amount=payment.amount,
        currency=payment.currency,
        metadata=payment.metadata,
    )
    payment.external_reference = session["gateway_payment_ref"]
    payment.save(update_fields=["external_reference", "updated_at"])
    payment.metadata["checkout_url"] = session["checkout_url"]
    payment.metadata["session_status"] = session["status"]
    payment.save(update_fields=["metadata", "updated_at"])
    return payment, False


@transaction.atomic
def verify_and_finalize(payment: CentralPayment):
    payment = CentralPayment.objects.select_for_update().select_related(
        "tenant", "module"
    ).get(pk=payment.pk)
    demo_issue = tenant_demo_block_reason(payment.tenant)
    if demo_issue:
        raise ValueError(demo_issue)

    if payment.transaction_status in {
        PaymentStatus.CAPTURED,
        PaymentStatus.PARTIALLY_REFUNDED,
        PaymentStatus.REFUNDED,
    }:
        return payment

    adapter = build_adapter(payment.gateway_name)
    response = adapter.verify_payment(external_reference=payment.external_reference)
    if getattr(settings, "PAYMENT_GATEWAY_MODE", "mock") == "live":
        if Decimal(str(response.get("amount", "0"))) != payment.amount or response.get("currency") != payment.currency or response.get("reference") != payment.payment_id:
            raise ValueError("Gateway amount, currency or payment reference does not match Central.")
    status = str(response.get("status") or "failed").lower()
    if status in {"captured", "paid", "success"}:
        payment.transaction_status = PaymentStatus.CAPTURED
        payment.refund_status = "none"
        payment.last_error = ""
        payment.save(update_fields=["transaction_status", "refund_status", "last_error", "updated_at"])
        tx = PaymentTransaction.objects.create(
            tenant=payment.tenant,
            module=payment.module,
            booking_ref=payment.booking_id or payment.payment_id,
            idempotency_key=payment.idempotency_key,
            external_payment_ref=payment.external_reference,
            gateway_txn_ref=payment.external_reference,
            currency=payment.currency,
            payment_channel="online",
            status="paid",
            booking_type="online",
            gross_amount=payment.amount,
            commission_amount=payment.commission_amount,
            net_amount=payment.business_share,
            occurred_at=timezone.now(),
            metadata={"payment_id": payment.payment_id, "gateway_name": payment.gateway_name},
        )
        enrich_and_post_transaction(tx)
        from .provider_updates import enqueue_payment_update
        if payment.booking_id: enqueue_payment_update(payment)
        from apps.marketplace.models import MarketplaceBooking
        MarketplaceBooking.objects.filter(booking_id=payment.booking_id,tenant=payment.tenant,module=payment.module).update(payment_status="paid")
    elif status in {"pending", "authorized"}:
        payment.transaction_status = PaymentStatus.AUTHORIZED if status == "authorized" else PaymentStatus.PENDING
        payment.save(update_fields=["transaction_status", "updated_at"])
    else:
        payment.transaction_status = PaymentStatus.FAILED
        payment.last_error = "Gateway verification failed."
        payment.save(update_fields=["transaction_status", "last_error", "updated_at"])
    return payment


@transaction.atomic
def refund_payment(payment: CentralPayment, amount: Decimal, reason: str, idempotency_key=""):
    payment = CentralPayment.objects.select_for_update().select_related("tenant").get(
        pk=payment.pk
    )
    demo_issue = tenant_demo_block_reason(payment.tenant)
    if demo_issue:
        raise ValueError(demo_issue)

    if len(idempotency_key) > 120: raise ValueError("Invalid refund idempotency key.")
    if idempotency_key:
        existing = payment.refunds.filter(idempotency_key=idempotency_key).first()
        if existing:
            if existing.amount != amount: raise ValueError("Refund key was already used for a different amount.")
            return existing, payment
    live = getattr(settings,"PAYMENT_GATEWAY_MODE","mock") == "live"
    if live and not idempotency_key: raise ValueError("A stable idempotency_key is required for live refunds.")
    if not amount.is_finite() or amount <= 0:
        raise ValueError("Refund amount must be a positive finite value.")
    if payment.transaction_status not in {
        PaymentStatus.CAPTURED,
        PaymentStatus.PARTIALLY_REFUNDED,
    }:
        raise ValueError("Only captured payments can be refunded.")
    already_refunded = payment.refunds.exclude(status__in=["failed","cancelled"]).aggregate(total=models.Sum("amount")).get("total") or Decimal("0.00")
    if amount > payment.amount - already_refunded:
        raise ValueError("Refund amount exceeds the remaining captured amount.")

    adapter = build_adapter(payment.gateway_name)
    kwargs = {"external_reference": payment.external_reference, "amount": amount, "reason": reason}
    if live: kwargs["idempotency_key"] = idempotency_key
    response = adapter.refund_payment(**kwargs)
    refund = CentralRefund.objects.create(
        payment=payment,
        idempotency_key=idempotency_key,
        refund_id=str(response.get("refund_reference") or f"rf_{uuid4().hex[:20]}"),
        amount=amount,
        is_partial=amount < payment.amount,
        reason=reason,
        status=str(response.get("status") or "processed"),
        metadata=response,
    )
    completed = refund.status in {"processed","succeeded"}
    if completed:
        from .refund_ledger import post_refund_ledger
        post_refund_ledger(refund)
        from .provider_updates import enqueue_payment_update
        if payment.booking_id: enqueue_payment_update(payment,"refund",refund.amount,refund.refund_id)
    refresh_refund_state(payment)
    return refund, payment


def refresh_refund_state(payment):
    total_refunded = payment.refunds.filter(status__in=["processed","succeeded"]).aggregate(total=models.Sum("amount")).get("total") or Decimal("0")
    if total_refunded >= payment.amount:
        payment.transaction_status = PaymentStatus.REFUNDED
        payment.refund_status = "full"
    elif total_refunded > 0:
        payment.transaction_status = PaymentStatus.PARTIALLY_REFUNDED
        payment.refund_status = "partial"
    else:
        payment.refund_status = "pending" if payment.refunds.filter(status="pending").exists() else "none"
    payment.save(update_fields=["transaction_status", "refund_status", "updated_at"])
    from apps.marketplace.models import MarketplaceBooking
    if total_refunded:
        MarketplaceBooking.objects.filter(booking_id=payment.booking_id,tenant=payment.tenant,module=payment.module).update(payment_status="refunded" if total_refunded>=payment.amount else "partially_refunded")


@transaction.atomic
def reconcile_refund(refund):
    payment=CentralPayment.objects.select_for_update().get(pk=refund.payment_id)
    refund=CentralRefund.objects.select_for_update().get(pk=refund.pk)
    if refund.status!="pending": return refund
    adapter=build_adapter(payment.gateway_name)
    checked=adapter.get_refund(refund.refund_id)
    if Decimal(checked["amount"])!=refund.amount or checked["currency"]!=payment.currency:
        raise ValueError("Gateway refund amount or currency does not match Central.")
    refund.status=checked["status"];refund.save(update_fields=["status"])
    if refund.status=="processed":
        from .refund_ledger import post_refund_ledger
        from .provider_updates import enqueue_payment_update
        post_refund_ledger(refund)
        if payment.booking_id:enqueue_payment_update(payment,"refund",refund.amount,refund.refund_id)
    refresh_refund_state(payment)
    return refund


def verify_webhook_signature(provider: str, raw_body: bytes, signature: str, timestamp: str = ""):
    config = GatewayConfig.objects.filter(provider=provider, is_enabled=True).first()
    secret = (config.get_webhook_secret() if config else "") or (
        config.get_secret_key() if config else ""
    )
    if not secret:
        return False
    if not timestamp or not signature:
        return False
    try:
        source_timestamp = datetime.fromtimestamp(int(timestamp), tz=dt_timezone.utc)
    except (ValueError, OverflowError, OSError):
        return False
    max_skew = int(getattr(settings, "PAYMENT_SIGNATURE_MAX_SKEW_SECONDS", 300))
    if abs((timezone.now() - source_timestamp).total_seconds()) > max_skew:
        return False
    payload = f"{timestamp}.".encode("utf-8") + raw_body
    expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature or "")


@transaction.atomic
def handle_webhook(provider: str, payload: dict, *, signature_valid: bool, detail: str = ""):
    event_id = str(payload.get("event_id") or payload.get("id") or "")
    if not signature_valid:
        return PaymentWebhookLog.objects.create(provider=provider,event_id="",signature_valid=False,payload=payload,processing_status="rejected",detail="Invalid signature")
    if event_id:
        existing = PaymentWebhookLog.objects.filter(provider=provider, event_id=event_id).first()
        if existing and existing.processing_status != "failed":
            return existing
        if existing:
            existing.delete()
    try:
        with transaction.atomic():
            log = PaymentWebhookLog.objects.create(
                provider=provider,
                event_id=event_id,
                signature_valid=signature_valid,
                payload=payload,
                processing_status="received",
                detail=detail,
            )
    except IntegrityError:
        return PaymentWebhookLog.objects.get(provider=provider, event_id=event_id)
    if not signature_valid:
        log.processing_status = "rejected"
        log.detail = "Invalid signature"
        log.save(update_fields=["processing_status", "detail"])
        return log

    payment_ref = str(payload.get("payment_ref") or payload.get("external_reference") or "")
    status = str(payload.get("status") or "").lower()
    payment = CentralPayment.objects.filter(
        models.Q(external_reference=payment_ref) | models.Q(payment_id=payment_ref)
    ).order_by("-id").first()
    if payment is None:
        log.processing_status = "ignored"
        log.detail = "Payment not found"
        log.save(update_fields=["processing_status", "detail"])
        return log

    if status in {"captured", "paid", "success"}:
        try:
            verify_and_finalize(payment)
            log.processing_status = "processed"
        except Exception as exc:
            log.processing_status = "failed"
            log.detail = str(exc)[:255]
    elif status in {"failed", "cancelled"}:
        payment.transaction_status = PaymentStatus.FAILED
        payment.save(update_fields=["transaction_status", "updated_at"])
        log.processing_status = "processed"
    else:
        log.processing_status = "ignored"
        log.detail = f"Unhandled status: {status}"
    log.save(update_fields=["processing_status", "detail"])
    return log
