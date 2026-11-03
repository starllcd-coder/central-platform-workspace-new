from django.db.models import Sum
from apps.orders.models import Order
from apps.payments.models import Payment

def apply_payment(data,amount):
    from django.conf import settings
    order=Order.objects.select_for_update().filter(order_no=data.get("booking_id")).first()
    if not order or data.get("currency")!=getattr(settings,"CENTRAL_CURRENCY","OMR"):raise ValueError("Order or currency does not match.")
    paid=order.payments.aggregate(total=Sum("amount"))["total"] or 0
    if data["kind"]=="payment" and paid+amount>order.total:raise ValueError("Payment exceeds the order total; review collection.")
    if data["kind"]=="refund" and amount>paid:raise ValueError("Refund exceeds the received order amount.")
    Payment.objects.create(order=order,method="CARD",amount=amount if data["kind"]=="payment" else -amount,reference=data["external_event_id"],note="Verified Central gateway update")
    order.refresh_payment_totals()
