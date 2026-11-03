from central_bridge.models import Delivery

def external_id(instance):
    return Delivery.objects.filter(booking_id=instance.pk).values_list("external_id", flat=True).first()

def mapped_status(value):
    return {'reserved': 'confirmed', 'checked_in': 'confirmed', 'checked_out': 'completed', 'cancelled': 'cancelled', 'no_show': 'cancelled'}.get(value)
