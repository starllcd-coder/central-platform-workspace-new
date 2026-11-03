from django.core.management.base import BaseCommand
from apps.paymentsvc.models import CentralPayment
from apps.paymentsvc.services import verify_and_finalize

class Command(BaseCommand):
    help = "Verify unsettled sessions against gateway APIs; never trust a browser return status."
    def add_arguments(self, parser):parser.add_argument("--limit",type=int,default=100)
    def handle(self,*args,**options):
        for payment in CentralPayment.objects.filter(transaction_status__in=["created","pending"]).exclude(external_reference="").order_by("updated_at")[:max(1,options["limit"])]:
            try:
                result=verify_and_finalize(payment)
                self.stdout.write(f"{payment.payment_id}: {result.transaction_status}")
            except Exception as exc:
                CentralPayment.objects.filter(pk=payment.pk).update(last_error=str(exc)[:255])
                self.stderr.write(f"{payment.payment_id}: verification failed")
        from apps.paymentsvc.models import CentralRefund
        from apps.paymentsvc.services import reconcile_refund
        for refund in CentralRefund.objects.filter(status="pending")[:max(1,options["limit"])]:
            try:
                reconcile_refund(refund)
                self.stdout.write(f"{refund.refund_id}: reconciled")
            except Exception:
                self.stderr.write(f"{refund.refund_id}: refund verification failed")
