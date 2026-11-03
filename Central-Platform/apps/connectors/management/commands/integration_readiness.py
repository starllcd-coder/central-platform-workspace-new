import json
from datetime import timedelta
from urllib.request import Request,urlopen
from urllib.parse import urlsplit
from django.conf import settings
from django.core.management.base import BaseCommand,CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.utils import timezone
from apps.connectors.models import AppConnector,ConnectorEvent
from apps.paymentsvc.models import GatewayConfig

class Command(BaseCommand):
    help="Read-only deployment preflight. Never creates bookings, payments or users."
    def add_arguments(self,parser):
        parser.add_argument("--check-http",action="store_true")
        parser.add_argument("--production",action="store_true")
    def handle(self,*args,**options):
        checks=[]
        def record(name,ok):checks.append({"check":name,"ok":bool(ok)})
        plan=MigrationExecutor(connection).migration_plan(MigrationExecutor(connection).loader.graph.leaf_nodes())
        record("database migrations applied",not plan)
        if plan:
            self.stdout.write(json.dumps(checks,indent=2));raise CommandError("Apply pending migrations before integration verification.")
        records=AppConnector.objects.filter(is_active=True,tenant__isnull=False).select_related("tenant","module")
        for connector in records:
            code=connector.module.code;name=connector.tenant.tenant_code+":"+code
            record(name+" provider and public URLs",bool(connector.base_url and connector.public_url))
            if options["production"]:record(name+" HTTPS",connector.base_url.startswith("https://") and connector.public_url.startswith("https://"))
            recent=ConnectorEvent.objects.filter(tenant=connector.tenant,module=connector.module,payload__event_name="connector.heartbeat",received_at__gte=timezone.now()-timedelta(minutes=15)).exists()
            record(name+" recent signed worker heartbeat",recent)
            if options["check_http"]:
                endpoint="/orders/central/health/" if code=="laundrex" else "/api/central/health/"
                try:
                    request=Request(connector.base_url.rstrip("/")+endpoint,headers={"X-Connector-Secret":settings.CONNECTOR_SHARED_SECRET})
                    with urlopen(request,timeout=10) as response:health=json.loads(response.read())
                    record(name+" authenticated provider identity",health.get("status")=="ok" and health.get("tenantCode")==connector.tenant.tenant_code and health.get("moduleCode")==code)
                    record(name+" sync enabled",health.get("syncEnabled"))
                    record(name+" linked SSO enabled",health.get("ssoEnabled") and health.get("linkedAccounts",0)>0)
                except Exception:record(name+" authenticated provider health",False)
        record("all three product connectors configured",set(records.values_list("module__code",flat=True))>={"drivesphere","staylux","laundrex"})
        if options["production"]:
            record("live payment mode",settings.PAYMENT_GATEWAY_MODE=="live")
            gateways=GatewayConfig.objects.filter(is_enabled=True,provider__in=["stripe","thawani"])
            record("payment gateway credentials",any(g.get_secret_key() and g.get_webhook_secret() for g in gateways))
            record("production email transport",not any(mode in settings.EMAIL_BACKEND for mode in ["console","locmem","dummy"]))
            record("Nexivo HTTPS origin",settings.NEXIVO_PUBLIC_URL.startswith("https://"))
        self.stdout.write(json.dumps(checks,indent=2))
        if not all(item["ok"] for item in checks):raise CommandError("Some integration checks are incomplete. This is not a live payment or end-to-end certification.")
