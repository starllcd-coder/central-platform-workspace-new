from apps.connectors.models import ConnectorEvent

def enqueue_payment_update(payment,kind="payment",amount=None,refund_id=None):
    identity=refund_id or payment.payment_id
    ConnectorEvent.objects.get_or_create(event_type="webhook.event",tenant=payment.tenant,module=payment.module,external_event_id="finance:"+identity,
        defaults={"status":"accepted","payload":{"event_name":"marketplace.payment.updated","tenant_code":payment.tenant.tenant_code,
            "module_code":payment.module.code,"external_event_id":identity,"payment_id":payment.payment_id,"booking_id":payment.booking_id,
            "kind":kind,"amount":str(amount if amount is not None else payment.amount),"currency":payment.currency}})
