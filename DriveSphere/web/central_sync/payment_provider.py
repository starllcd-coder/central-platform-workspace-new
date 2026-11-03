import hashlib
from django.utils import timezone
from django.db.models import Sum
from central_bridge.models import Delivery
from apps.bookings.models import Booking
from apps.payments.models import Payment,Refund

def apply_payment(data,amount):
    delivery=Delivery.objects.filter(external_id=data.get("booking_id")).first()
    booking=Booking.objects.select_for_update().filter(pk=delivery.booking_id).first() if delivery else None
    if not booking or data.get("currency")!=booking.currency_code:raise ValueError("Booking or currency does not match.")
    key="central:"+str(data.get("payment_id") or "")
    if data["kind"]=="payment":
        paid=Payment.objects.filter(booking=booking,status="PAID").aggregate(total=Sum("amount"))["total"] or 0
        if paid+amount>booking.total_amount:raise ValueError("Payment exceeds the outstanding booking amount; review collection.")
        Payment.objects.create(booking=booking,branch=booking.branch,receipt_number="CP-"+hashlib.sha256(key.encode()).hexdigest()[:24],idempotency_key=key,
            payment_date=timezone.localdate(),method="CARD",amount=amount,currency_code=booking.currency_code,status="PAID",notes="Verified Central gateway payment")
    else:
        payment=Payment.objects.select_for_update().filter(booking=booking,idempotency_key=key).first()
        if not payment:raise ValueError("Original Central payment is not available yet.")
        refunded=payment.refunds.filter(status="REFUNDED").aggregate(total=Sum("amount"))["total"] or 0
        if refunded+amount>payment.amount:raise ValueError("Refund exceeds original payment.")
        Refund.objects.create(payment=payment,branch=booking.branch,refund_number="CR-"+hashlib.sha256(data["external_event_id"].encode()).hexdigest()[:24],idempotency_key="central:"+data["external_event_id"],refund_date=timezone.localdate(),method="CARD",amount=amount,currency_code=booking.currency_code,status="REFUNDED")
