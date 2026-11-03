import json
import time
from unittest.mock import patch,MagicMock
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase,override_settings
from django.urls import reverse
from .models import CentralAccountLink

@override_settings(CENTRAL_SSO_ENABLED=True,CENTRAL_TENANT_CODE="ONE",CENTRAL_MODULE_CODE="laundrex",CENTRAL_PLATFORM_URL="https://central.example")
class SharedSignInTests(TestCase):
    def setUp(self):
        self.user=get_user_model().objects.create_user(username="linked",email="linked@example.com",password="local-test-password")
        CentralAccountLink.objects.create(central_user_id="123",user=self.user)
        self.claims={"uid":123,"kind":"login-ticket","tenant_code":"ONE","module_codes":["laundrex"],"state":"test-state"}
        session=self.client.session;session["central_sso_state"]="test-state";session["central_sso_deadline"]=time.time()+300;session.save()

    def response(self,claims):
        response=MagicMock();response.read.return_value=json.dumps({"active":True,"claims":claims}).encode();return response

    @patch("central_sync.sso_context.context_for",return_value={})
    @patch("central_sync.sso.urlopen")
    def test_existing_local_identity_signs_in_without_role_changes_and_state_cannot_be_reused(self,remote,context):
        remote.return_value.__enter__.return_value=self.response(self.claims)
        before=(self.user.is_staff,self.user.is_superuser)
        response=self.client.post(reverse("orders:central-sso"),json.dumps({"token":"ticket"}),content_type="application/json")
        self.assertEqual(response.status_code,200,response.content)
        self.user.refresh_from_db();self.assertEqual((self.user.is_staff,self.user.is_superuser),before)
        self.assertEqual(self.client.post(reverse("orders:central-sso"),json.dumps({"token":"ticket"}),content_type="application/json").status_code,403)

    @patch("central_sync.sso.urlopen")
    def test_wrong_tenant_or_unlinked_identity_cannot_sign_in(self,remote):
        for claims in [{**self.claims,"tenant_code":"OTHER"},{**self.claims,"uid":999},{**self.claims,"state":"wrong-state"}]:
            remote.return_value.__enter__.return_value=self.response(claims)
            self.assertEqual(self.client.post(reverse("orders:central-sso"),json.dumps({"token":"ticket"}),content_type="application/json").status_code,403)
        self.assertNotIn("_auth_user_id",self.client.session)

    @patch("central_sync.auth_backend.urlopen")
    def test_mapped_central_credentials_preserve_local_password_and_permissions(self,remote):
        from central_sync.auth_backend import MappedCentralBackend
        response=MagicMock();response.read.return_value=json.dumps({"user":{"id":"123"},"accessToken":"central-token"}).encode()
        remote.return_value.__enter__.return_value=response
        identifier=getattr(self.user,self.user.USERNAME_FIELD)
        authenticated=MappedCentralBackend().authenticate(None,username=identifier,password="central-password")
        self.assertEqual(authenticated.pk,self.user.pk)
        self.user.refresh_from_db();self.assertTrue(self.user.check_password("local-test-password"))
        response.read.return_value=json.dumps({"user":{"id":"different"}}).encode()
        self.assertIsNone(MappedCentralBackend().authenticate(None,username=identifier,password="central-password"))
