from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum
from central_bridge.models import Delivery
from bookings.models import Booking
from billing.models import Invoice,InvoiceLine,Payment

def apply_payment(data,amount):
    delivery=Delivery.objects.filter(external_id=data.get("booking_id")).first()
    booking=Booking.objects.select_for_update().filter(pk=delivery.booking_id).first() if delivery else None
    if not booking or data.get("currency")!=booking.property_profile.currency:raise ValueError("Booking or currency does not match.")
    invoice=Invoice.objects.select_for_update().filter(booking=booking).first()
    if not invoice:
        if data["kind"]=="refund":raise ValueError("Original invoice is not available yet.")
        invoice=Invoice.objects.create(property_profile=booking.property_profile,booking=booking,guest=booking.guest,status="issued",issue_date=timezone.localdate(),due_date=timezone.localdate(),currency=booking.property_profile.currency)
        InvoiceLine.objects.create(invoice=invoice,description="Nexivo accommodation",quantity=1,unit_price=booking.locked_total or booking.estimate_total())
        invoice.ensure_invoice_no();invoice.recalc_and_save()
    invoice.recalc_and_save()
    if data["kind"]=="payment" and amount>invoice.balance_due:raise ValueError("Payment exceeds the outstanding invoice amount; review collection.")
    if data["kind"]=="refund" and amount>invoice.amount_paid:raise ValueError("Refund exceeds the received invoice amount.")
    Payment.objects.create(invoice=invoice,property_profile=booking.property_profile,method="card",direction="in" if data["kind"]=="payment" else "out",amount=amount,reference=data["external_event_id"],paid_at=timezone.now(),notes="Verified Central gateway update")
    invoice.recalc_and_save()
    if data["kind"]=="refund" and invoice.balance_due>0:invoice.status="issued";invoice.save(update_fields=["status"])
