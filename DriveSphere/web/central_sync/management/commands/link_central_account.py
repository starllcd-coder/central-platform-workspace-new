from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand,CommandError
from central_sync.models import CentralAccountLink
class Command(BaseCommand):
    help="Link a known Central identity to an existing local account without changing its roles."
    def add_arguments(self,parser):
        parser.add_argument("central_user_id")
        parser.add_argument("local_user_id",type=int)
    def handle(self,*args,**options):
        user=get_user_model().objects.filter(pk=options["local_user_id"],is_active=True).first()
        if not user:raise CommandError("Active local user not found.")
        existing=CentralAccountLink.objects.filter(central_user_id=options["central_user_id"]).first()
        if existing and existing.user_id!=user.pk:raise CommandError("Identity already maps to another local account; review it before changing the link.")
        CentralAccountLink.objects.update_or_create(central_user_id=options["central_user_id"],defaults={"user":user,"is_active":True})
        self.stdout.write("Account link saved; local permissions were not changed.")
