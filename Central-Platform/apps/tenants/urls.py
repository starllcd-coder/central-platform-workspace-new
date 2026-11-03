from django.urls import path

from .views import (
    agreement_accept,
    agreement_list,
    demo_request_create,
    demo_request_convert_to_paid,
    demo_request_list,
    demo_request_review,
    my_demo_requests,
    tenant_create,
    tenant_demo_create,
    tenant_branding_domain_refresh_token,
    tenant_branding_domain_status_api,
    tenant_branding_domain_verify,
    tenant_branding_manage,
    tenant_list,
    tenant_modules_manage,
    tenant_structure_manage,
    tenant_users_manage,
)

urlpatterns = [
    path("", tenant_list, name="tenant-list"),
    path("new/", tenant_create, name="tenant-create"),
    path("demo/new/", tenant_demo_create, name="tenant-demo-create"),
    path("demo/requests/new/", demo_request_create, name="demo-request-create"),
    path("demo/requests/mine/", my_demo_requests, name="my-demo-requests"),
    path("demo/requests/", demo_request_list, name="demo-request-list"),
    path("demo/requests/<int:request_id>/review/", demo_request_review, name="demo-request-review"),
    path(
        "demo/requests/<int:request_id>/convert-to-paid/",
        demo_request_convert_to_paid,
        name="demo-request-convert-to-paid",
    ),
    path("<int:tenant_id>/modules/", tenant_modules_manage, name="tenant-modules-manage"),
    path("<int:tenant_id>/users/", tenant_users_manage, name="tenant-users-manage"),
    path("<int:tenant_id>/structure/", tenant_structure_manage, name="tenant-structure-manage"),
    path("<int:tenant_id>/branding/", tenant_branding_manage, name="tenant-branding-manage"),
    path(
        "<int:tenant_id>/branding/domain/refresh-token/",
        tenant_branding_domain_refresh_token,
        name="tenant-branding-domain-refresh-token",
    ),
    path(
        "<int:tenant_id>/branding/domain/verify/",
        tenant_branding_domain_verify,
        name="tenant-branding-domain-verify",
    ),
    path(
        "<int:tenant_id>/branding/api/domain-status/",
        tenant_branding_domain_status_api,
        name="tenant-branding-domain-status-api",
    ),
    path("agreements/", agreement_list, name="tenant-agreements"),
    path("agreements/<int:doc_id>/accept/", agreement_accept, name="tenant-agreement-accept"),
]
