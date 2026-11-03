from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.tenants.domain_verification import verify_branding_custom_domain
from apps.tenants.models import TenantBranding


class Command(BaseCommand):
    help = "Run DNS verification checks for tenant custom domains."

    def add_arguments(self, parser):
        parser.add_argument("--tenant-id", type=int, default=0)
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--include-verified", action="store_true")

    def handle(self, *args, **options):
        tenant_id = int(options["tenant_id"] or 0)
        limit = max(1, int(options["limit"] or 100))
        include_verified = bool(options["include_verified"])

        qs = TenantBranding.objects.filter(is_active=True).exclude(custom_domain="")
        if tenant_id:
            qs = qs.filter(tenant_id=tenant_id)
        if not include_verified:
            qs = qs.filter(
                Q(domain_verification_status__in=["pending", "failed", "not_configured"])
                | Q(domain_verified_at__isnull=True)
            )

        rows = list(qs.select_related("tenant")[:limit])
        if not rows:
            self.stdout.write("No custom domains to verify.")
            return

        verified = 0
        failed = 0
        for row in rows:
            result = verify_branding_custom_domain(row)
            if result["verified"]:
                verified += 1
            else:
                failed += 1
        self.stdout.write(
            f"verify_custom_domains checked={len(rows)} verified={verified} failed={failed}"
        )
