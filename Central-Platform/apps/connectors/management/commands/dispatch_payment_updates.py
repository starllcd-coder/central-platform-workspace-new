from datetime import timedelta
from django.db.models import F,Q
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.connectors.models import ConnectorEvent
from apps.connectors.client import provider_request

class Command(BaseCommand):
    help="Deliver verified payment/refund updates to existing provider accounting records."
    def add_arguments(self,parser):parser.add_argument("--limit",type=int,default=100)
    def handle(self,*args,**options):
        events=ConnectorEvent.objects.filter(payload__event_name="marketplace.payment.updated",status__in=["accepted","dispatch_failed","dispatching"]).filter(Q(next_retry_at__isnull=True)|Q(next_retry_at__lte=timezone.now())).select_related("tenant","module").order_by("id")[:max(1,options["limit"])]
        for event in events:
            claimed=ConnectorEvent.objects.filter(pk=event.pk,status__in=["accepted","dispatch_failed","dispatching"]).filter(Q(next_retry_at__isnull=True)|Q(next_retry_at__lte=timezone.now())).update(status="dispatching",next_retry_at=timezone.now()+timedelta(minutes=5),dispatch_attempts=F("dispatch_attempts")+1)
            if not claimed:continue
            event.refresh_from_db()
            try:
                provider_request(event.tenant,event.module,"payments",event.payload)
                event.status="dispatched";event.last_error="";event.next_retry_at=None
            except Exception as exc:
                event.last_error=str(exc)[:500];event.status="dead_letter" if event.dispatch_attempts>=8 else "dispatch_failed"
                event.next_retry_at=timezone.now()+timedelta(seconds=min(60*2**min(event.dispatch_attempts,6),3600))
            event.save(update_fields=["status","last_error","next_retry_at"])
            self.stdout.write(f"{event.external_event_id}: {event.status}")
