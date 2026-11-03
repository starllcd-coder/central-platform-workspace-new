from django.urls import path

from .views import (
    BusinessInvitationConfirmView,
    sso_token_introspect_api,
    sso_token_issue_api,
    reauth_verify,
    switch_module,
    switch_tenant,
    two_factor_enable,
    two_factor_regenerate_backup_codes,
    two_factor_setup,
    two_factor_verify,
)

urlpatterns = [
    path(
        "invitations/<uidb64>/<token>/",
        BusinessInvitationConfirmView.as_view(),
        name="business-invitation-confirm",
    ),
    path("api/sso/token/", sso_token_issue_api, name="sso-token-issue-api"),
    path("api/sso/introspect/", sso_token_introspect_api, name="sso-token-introspect-api"),
    path("switch-tenant/", switch_tenant, name="switch-tenant"),
    path("switch-module/", switch_module, name="switch-module"),
    path("2fa/setup/", two_factor_setup, name="two-factor-setup"),
    path("2fa/verify/", two_factor_verify, name="two-factor-verify"),
    path("2fa/enable/", two_factor_enable, name="two-factor-enable"),
    path("reauth/", reauth_verify, name="reauth-verify"),
    path(
        "2fa/regenerate-backup-codes/",
        two_factor_regenerate_backup_codes,
        name="two-factor-regenerate-backup-codes",
    ),
]
