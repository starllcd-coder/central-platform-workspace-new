from dataclasses import dataclass

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.tenants.models import Module

from .models import MembershipRole, Role, TenantMembership


@dataclass
class BusinessInvitationResult:
    user: object
    membership: TenantMembership
    user_created: bool
    invitation_required: bool


def _unique_username(email):
    User = get_user_model()
    base = email[:140]
    username = base
    suffix = 1
    while User.objects.filter(username__iexact=username).exists():
        suffix += 1
        username = f"{base[:140 - len(str(suffix))]}-{suffix}"
    return username


def _ensure_access_role(access_level):
    if access_level == "owner":
        role, _ = Role.objects.get_or_create(
            code="tenant.owner",
            defaults={"name": "Business Owner", "scope": "tenant", "is_active": True},
        )
        return role
    role, _ = Role.objects.get_or_create(
        code="tenant.member",
        defaults={"name": "Business Member", "scope": "tenant", "is_active": True},
    )
    return role


def _send_business_invitation(*, user, tenant, request, invitation_required):
    if invitation_required:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        path = reverse("business-invitation-confirm", kwargs={"uidb64": uid, "token": token})
        subject = f"Set up your {tenant.name} account"
        body = (
            f"You have been invited to access {tenant.name} ({tenant.tenant_code}) "
            "on Central Platform.\n\n"
            f"Set your password using this secure link:\n{request.build_absolute_uri(path)}\n\n"
            "The link is single-use. Contact Central Platform staff if it expires."
        )
    else:
        subject = f"Access granted to {tenant.name}"
        body = (
            f"Your existing Central Platform account now has access to "
            f"{tenant.name} ({tenant.tenant_code}).\n\n"
            f"Sign in here: {request.build_absolute_uri(reverse('login'))}"
        )
    send_mail(subject, body, None, [user.email], fail_silently=True)


@transaction.atomic
def invite_business_user_to_tenant(*, tenant, email, full_name="", access_level="owner", request):
    User = get_user_model()
    normalized_email = str(email or "").strip().lower()
    if not normalized_email:
        raise ValueError("A business user email address is required.")

    user = User.objects.filter(email__iexact=normalized_email).first()
    user_created = user is None
    if user is None:
        name_parts = str(full_name or "").strip().split(None, 1)
        user = User(
            username=_unique_username(normalized_email),
            email=normalized_email,
            first_name=name_parts[0][:150] if name_parts else "",
            last_name=name_parts[1][:150] if len(name_parts) > 1 else "",
            is_active=True,
        )
        user.set_unusable_password()
        user.save()
    elif not user.is_active:
        raise ValueError("This email belongs to a disabled Central Platform account.")

    invitation_required = not user.has_usable_password()
    membership, _ = TenantMembership.objects.get_or_create(
        user=user,
        tenant=tenant,
        defaults={"status": "invited" if invitation_required else "active"},
    )
    target_status = "invited" if invitation_required else "active"
    if membership.status != target_status:
        membership.status = target_status
        membership.save(update_fields=["status"])

    role = _ensure_access_role(access_level)
    module = Module.objects.filter(code__iexact=tenant.module_type).first()
    MembershipRole.objects.get_or_create(membership=membership, role=role, module=module)

    transaction.on_commit(
        lambda: _send_business_invitation(
            user=user,
            tenant=tenant,
            request=request,
            invitation_required=invitation_required,
        ),
        robust=True,
    )
    return BusinessInvitationResult(user, membership, user_created, invitation_required)
