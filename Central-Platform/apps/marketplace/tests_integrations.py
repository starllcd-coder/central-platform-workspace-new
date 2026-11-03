import json
from decimal import Decimal
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.db import transaction
from apps.accounts.models import Role, MembershipRole, TenantMembership
from apps.tenants.models import Tenant, Module, TenantModule, MarketplaceListing
from apps.connectors.inventory import apply_inventory
from .models import MarketplaceBooking
from .views import _issue_token

class IntegrationTests(TestCase):
    def setUp(self):
        self.tenant=Tenant.objects.create(tenant_code="ONE",name="One",status="active",currency="OMR")
        self.other=Tenant.objects.create(tenant_code="TWO",name="Two",status="active",currency="OMR")
        self.module=Module.objects.create(code="drivesphere",name="DriveSphere")
        TenantModule.objects.create(tenant=self.tenant,module=self.module,enabled=True,marketplace_enabled=True)
        self.listing=MarketplaceListing.objects.create(tenant=self.tenant,module=self.module,provider_resource_id="CAR-ONE",base_price="20.125")
        self.user=get_user_model().objects.create_user(username="owner@example.com",email="owner@example.com",password="strong-password-123")
        membership=TenantMembership.objects.create(user=self.user,tenant=self.tenant)
        role=Role.objects.create(code="tenant.owner",name="Owner")
        MembershipRole.objects.create(membership=membership,role=role)
        self.auth={"HTTP_AUTHORIZATION":"Bearer "+_issue_token(self.user.pk,self.user.email)}

    def test_multiple_resources_keep_existing_url(self):
        previous=self.listing.public_slug
        second=MarketplaceListing.objects.create(tenant=self.tenant,module=self.module,provider_resource_id="CAR-TWO",base_price="30")
        self.assertNotEqual(previous,second.public_slug)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.public_slug,previous)

    def test_inventory_events_do_not_allow_currency_changes_or_stale_overwrites(self):
        data={"resource_id":"CAR-TWO","name":"Two","base_price":"30.125","currency":"OMR","active":True,"updated_at":timezone.now().isoformat()}
        payload={"event_name":"marketplace.resource.updated","data":data}
        with transaction.atomic():apply_inventory(payload,self.tenant,self.module)
        resource=MarketplaceListing.objects.get(provider_resource_id="CAR-TWO")
        self.assertEqual(resource.base_price,Decimal("30.125"))
        with transaction.atomic():apply_inventory({**payload,"data":{**data,"base_price":"1"}},self.tenant,self.module)
        resource.refresh_from_db();self.assertEqual(resource.base_price,Decimal("30.125"))
        with self.assertRaises(ValueError), transaction.atomic():apply_inventory({**payload,"data":{**data,"currency":"USD"}},self.tenant,self.module)

    def test_partner_scope_does_not_expose_other_tenant(self):
        MarketplaceBooking.objects.create(booking_id="PRIVATE",tenant=self.other,module=self.module,customer_name="Other Customer")
        MarketplaceBooking.objects.create(booking_id="OWN",tenant=self.tenant,module=self.module,customer_name="Own Customer")
        response=self.client.get(reverse("provider-dashboard"),**self.auth)
        self.assertEqual(response.status_code,200)
        self.assertEqual([r["id"] for r in response.json()["bookings"]],["OWN"])
        self.assertEqual(self.client.get(reverse("admin-dashboard"),**self.auth).status_code,403)
        TenantMembership.objects.filter(user=self.user).update(status="suspended")
        self.assertEqual(self.client.get(reverse("provider-dashboard"),**self.auth).json()["bookings"],[])

    @override_settings(MARKETPLACE_REQUIRE_QUOTES=True)
    @patch("apps.marketplace.quotes.provider_request")
    def test_quote_is_bound_to_dates_and_uses_three_decimal_provider_amount(self, provider):
        provider.return_value={"ok":True,"amount":"40.250","currency":"OMR"}
        body={"listingSlug":self.listing.public_slug,"pickupDate":"2027-01-01","returnDate":"2027-01-03","fullName":"Customer","email":"customer@example.com"}
        response=self.client.post(reverse("marketplace-quotes"),json.dumps(body),content_type="application/json")
        self.assertEqual(response.status_code,200,response.content)
        token=response.json()["quoteToken"]
        changed=self.client.post(reverse("marketplace-api-bookings"),json.dumps({**body,"returnDate":"2027-01-04","quoteToken":token}),content_type="application/json")
        self.assertEqual(changed.status_code,422)
        booked=self.client.post(reverse("marketplace-api-bookings"),json.dumps({**body,"quoteToken":token}),content_type="application/json")
        self.assertEqual(booked.status_code,201,booked.content)
        self.assertEqual(MarketplaceBooking.objects.get().total_amount,Decimal("40.250"))

    def test_shared_login_tickets_are_short_lived_state_bound_and_single_use(self):
        from urllib.parse import urlsplit,parse_qs
        from apps.connectors.models import AppConnector
        AppConnector.objects.create(tenant=self.tenant,module=self.module,base_url="https://drive.example",public_url="https://drive.example")
        state="test-state-"+"x"*32
        response=self.client.post(reverse("provider-sso-ticket"),json.dumps({"tenantCode":"ONE","moduleCode":"drivesphere","state":state}),content_type="application/json",**self.auth)
        self.assertEqual(response.status_code,200,response.content)
        token=parse_qs(urlsplit(response.json()["launchUrl"]).fragment)["central_sso"][0]
        from django.conf import settings
        payload=json.dumps({"token":token,"consume":True})
        url="/accounts/api/sso/introspect/"
        first=self.client.post(url,payload,content_type="application/json",HTTP_X_CONNECTOR_SECRET=settings.CONNECTOR_SHARED_SECRET)
        self.assertTrue(first.json()["active"])
        self.assertEqual(first.json()["claims"]["state"],state)
        self.assertFalse(self.client.post(url,payload,content_type="application/json",HTTP_X_CONNECTOR_SECRET=settings.CONNECTOR_SHARED_SECRET).json()["active"])

    def test_provider_can_log_in_by_email_when_django_username_differs(self):
        self.user.username="different-central-username";self.user.save(update_fields=["username"])
        response=self.client.post(reverse("marketplace-api-provider-login"),json.dumps({"email":self.user.email,"password":"strong-password-123"}),content_type="application/json")
        self.assertEqual(response.status_code,200,response.content)
        self.assertEqual(response.json()["user"]["role"],"partner")
