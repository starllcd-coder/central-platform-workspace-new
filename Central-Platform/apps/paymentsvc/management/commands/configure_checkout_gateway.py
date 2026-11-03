import os
from django.core.management.base import BaseCommand,CommandError
from apps.paymentsvc.models import GatewayConfig

class Command(BaseCommand):
    help="Store gateway keys from environment variables using Central's existing encryption. Does not enable live payment mode."
    def add_arguments(self,parser):
        parser.add_argument("provider",choices=["stripe","thawani"])
        parser.add_argument("--enable",action="store_true")
        parser.add_argument("--production",action="store_true")
    def handle(self,*args,**options):
        provider=options["provider"];prefix=provider.upper()
        secret=os.getenv(prefix+"_SECRET_KEY","");webhook=os.getenv(prefix+"_WEBHOOK_SECRET","")
        if not secret or not webhook:raise CommandError(f"Set {prefix}_SECRET_KEY and {prefix}_WEBHOOK_SECRET in the deployment environment.")
        config,_=GatewayConfig.objects.get_or_create(provider=provider)
        config.set_secret_key(secret);config.set_webhook_secret(webhook);config.is_enabled=options["enable"]
        if provider=="thawani":
            config.public_key=os.getenv("THAWANI_PUBLIC_KEY","")
            if not config.public_key:raise CommandError("THAWANI_PUBLIC_KEY is required.")
            config.api_base_url="https://checkout.thawani.om" if options["production"] else "https://uatcheckout.thawani.om"
            config.supports_partial_refund=False
            config.supports_card_guarantee=False
            config.settings_json={**config.settings_json,"currencies":["OMR"]}
        config.save();self.stdout.write("Gateway configuration saved. Keys were not printed. Verify sandbox checkout before selecting live mode.")
