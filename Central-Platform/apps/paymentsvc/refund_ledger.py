from decimal import Decimal
from django.db import transaction
from apps.billing.models import PaymentTransaction, LedgerEntry, RefundRecord
from apps.billing.services import get_platform_wallet, post_wallet_transaction

def post_refund_ledger(refund):
    payment=refund.payment
    tx=PaymentTransaction.objects.select_for_update().filter(tenant=payment.tenant,external_payment_ref=payment.external_reference).first()
    if not tx:raise ValueError("Captured transaction is missing; reconcile before posting a refund.")
    if refund.metadata.get("ledger_posted"):return
    total=tx.refunded_amount+refund.amount
    if total>tx.gross_amount:raise ValueError("Refund exceeds the recorded captured transaction.")
    original=tx.metadata.get("refund_basis") or {"commission":str(tx.commission_amount),"net":str(tx.net_amount)}
    tx.metadata={**tx.metadata,"refund_basis":original}
    ratio=refund.amount/tx.gross_amount
    reversal=(Decimal(original["commission"])*ratio).quantize(Decimal("0.001"))
    recovery=(Decimal(original["net"])*ratio).quantize(Decimal("0.001"))
    settled=tx.settlement_state=="settled"
    RefundRecord.objects.create(transaction=tx,refund_type="full" if refund.amount==tx.gross_amount else "partial",
        refund_percent=(ratio*100).quantize(Decimal("0.01")),customer_refund_amount=refund.amount,commission_reversal_amount=reversal,
        business_recovery_amount=recovery if settled else 0,status="review" if settled else "processed",reason=refund.reason)
    LedgerEntry.objects.create(tenant=tx.tenant,transaction=tx,entry_type="refund",debit=0,credit=refund.amount,currency=tx.currency,notes=f"Gateway refund {refund.refund_id}")
    if reversal:
        LedgerEntry.objects.create(tenant=tx.tenant,transaction=tx,entry_type="commission_reversal",debit=reversal,credit=0,currency=tx.currency)
        post_wallet_transaction(wallet=get_platform_wallet(currency=tx.currency),tx_type="debit",reason="adjustment",amount=reversal,tenant=tx.tenant,payment_transaction=tx,notes=f"Gateway refund {refund.refund_id}")
    if settled:
        LedgerEntry.objects.create(tenant=tx.tenant,transaction=tx,entry_type="refund_recovery_due",debit=recovery,credit=0,currency=tx.currency)
        tx.lifecycle_state="review"
    else:
        tx.net_amount=max(Decimal("0"),tx.net_amount-recovery)
        tx.commission_amount=max(Decimal("0"),tx.commission_amount-reversal)
        if total==tx.gross_amount:tx.settlement_state="excluded"
    tx.refunded_amount=total
    tx.status="refunded" if total==tx.gross_amount else "paid"
    tx.save()
    refund.metadata={**refund.metadata,"ledger_posted":True};refund.save(update_fields=["metadata"])
