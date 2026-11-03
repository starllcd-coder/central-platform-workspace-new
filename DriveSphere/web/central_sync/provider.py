from central_bridge.models import Delivery

def external_id(instance):
    return Delivery.objects.filter(booking_id=instance.pk).values_list("external_id", flat=True).first()

def mapped_status(value):
    return {'DRAFT': 'pending', 'CONFIRMED': 'confirmed', 'UPCOMING': 'confirmed', 'CHECKED_OUT': 'confirmed', 'RETURNED': 'completed', 'CLOSED': 'completed', 'CANCELLED': 'cancelled'}.get(value)
