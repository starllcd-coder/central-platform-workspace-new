def external_id(instance):
    return instance.order_no if instance.order_no.startswith("NXV-") else None

def mapped_status(value):
    return {"CANCELLED": "cancelled", "DELIVERED": "completed"}.get(value, "confirmed")
