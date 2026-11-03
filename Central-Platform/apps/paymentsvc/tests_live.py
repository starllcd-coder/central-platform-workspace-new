import hashlib
import hmac
import json
import time
from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase,SimpleTestCase,override_settings
from django.urls import reverse
from apps.tenants.models import Tenant,Module,TenantModule
from apps.billing.models import PaymentTransaction,LedgerEntry
from .models import CentralPayment,GatewayConfig,CentralRefund
from .live_adapters import StripeLiveAdapter,ThawaniLiveAdapter,minor_units
from .services import verify_and_finalize,refund_payment,reconcile_refund

class Config:
    api_base_url="https://uatcheckout.thawani.om";public_key="pk_test";settings_json={}
    def get_secret_key(self):return "sk_test_only"

class GatewayContractTests(SimpleTestCase):
    def test_minor_unit_precision_is_never_silently_rounded(self):
        self.assertEqual(minor_units(Decimal("2.125"),"OMR"),2125)
        self.assertEqual(minor_units(Decimal("12.34"),"USD"),1234)
        with self.assertRaises(ValueError):minor_units(Decimal("12.345"),"USD")

    @patch.object(StripeLiveAdapter,"request",return_value={"id":"cs_test","url":"https://checkout.stripe.com/c/pay/test"})
    def test_stripe_checkout_uses_server_amount_and_stable_idempotency(self,request):
        result=StripeLiveAdapter(Config()).create_payment_session(payment_id="pay-test",amount=Decimal("12.34"),currency="USD",metadata={"success_url":"https://nexivo.test/ok","cancel_url":"https://nexivo.test/cancel"})
        self.assertEqual(result["gateway_payment_ref"],"cs_test")
        self.assertEqual(request.call_args.args[1]["line_items[0][price_data][unit_amount]"],1234)
        self.assertEqual(request.call_args.kwargs["key"],"pay-test")

    @patch.object(ThawaniLiveAdapter,"request",return_value={"success":True,"data":{"session_id":"checkout_test"}})
    def test_thawani_checkout_uses_baisa_and_hosted_redirect(self,request):
        result=ThawaniLiveAdapter(Config()).create_payment_session(payment_id="pay-test",amount=Decimal("2.125"),currency="OMR",metadata={"success_url":"https://nexivo.test/ok","cancel_url":"https://nexivo.test/cancel"})
        self.assertEqual(request.call_args.args[1]["products"][0]["unit_amount"],2125)
        self.assertTrue(result["checkout_url"].startswith("https://uatcheckout.thawani.om/pay/"))

@override_settings(PAYMENT_GATEWAY_MODE="live")
class LivePaymentSecurityTests(TestCase):
    def setUp(self):
        self.tenant=Tenant.objects.create(tenant_code="PAY-LIVE",name="Payment test",currency="USD",status="active")
        self.module=Module.objects.create(code="drivesphere",name="DriveSphere")
        TenantModule.objects.create(tenant=self.tenant,module=self.module,enabled=True)
        self.config=GatewayConfig(provider="stripe",is_enabled=True)
        self.config.set_secret_key("sk_test_only");self.config.set_webhook_secret("whsec_test_only");self.config.save()
        self.payment=CentralPayment.objects.create(payment_id="pay-test",external_reference="cs_test",tenant=self.tenant,module=self.module,amount="12.340",currency="USD",gateway_name="stripe",transaction_status="pending",business_share="12.340")
        self.verified={"status":"captured","amount":"12.340","currency":"USD","reference":"pay-test"}

    @patch.object(StripeLiveAdapter,"verify_payment")
    def test_amount_mismatch_never_posts_a_paid_transaction(self,verify):
        verify.return_value={**self.verified,"amount":"1"}
        with self.assertRaises(ValueError):verify_and_finalize(self.payment)
        self.assertFalse(PaymentTransaction.objects.exists())

    @patch.object(StripeLiveAdapter,"verify_payment")
    def test_native_webhook_rejects_forgery_and_processes_valid_duplicate_once(self,verify):
        verify.return_value=self.verified
        raw=json.dumps({"id":"evt_test","type":"checkout.session.completed","data":{"object":{"id":"cs_test","payment_status":"paid"}}}).encode()
        url=reverse("paymentsvc-webhook-stripe")
        self.assertEqual(self.client.post(url,raw,content_type="application/json",HTTP_STRIPE_SIGNATURE="t=0,v1=forged").status_code,403)
        ts=str(int(time.time()));sig=hmac.new(b"whsec_test_only",ts.encode()+b"."+raw,hashlib.sha256).hexdigest()
        for _ in range(2):self.assertEqual(self.client.post(url,raw,content_type="application/json",HTTP_STRIPE_SIGNATURE=f"t={ts},v1={sig}").status_code,200)
        self.assertEqual(PaymentTransaction.objects.count(),1)

    @patch.object(StripeLiveAdapter,"verify_payment")
    @patch.object(StripeLiveAdapter,"refund_payment")
    def test_refunds_are_idempotent_and_pending_is_not_treated_as_refunded(self,refund,verify):
        verify.return_value=self.verified
        payment=verify_and_finalize(self.payment)
        refund.return_value={"refund_reference":"re_test","status":"pending"}
        row,payment=refund_payment(payment,Decimal("6.170"),"requested_by_customer","refund-key")
        self.assertEqual(payment.transaction_status,"captured")
        same,_=refund_payment(payment,Decimal("6.170"),"requested_by_customer","refund-key")
        self.assertEqual(same.pk,row.pk);refund.assert_called_once()
        with patch.object(StripeLiveAdapter,"get_refund",return_value={"status":"processed","amount":"6.170","currency":"USD"}):
            reconcile_refund(row)
            reconcile_refund(row)
        payment.refresh_from_db()
        self.assertEqual(payment.transaction_status,"partially_refunded")
        self.assertEqual(LedgerEntry.objects.filter(entry_type="refund").count(),1)
