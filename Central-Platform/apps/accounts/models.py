from django.conf import settings
from django.db import models

from apps.tenants.models import Module, Tenant


class Permission(models.Model):
    code = models.CharField(max_length=120, unique=True)
    name = models.CharField(max_length=180)
    description = models.CharField(max_length=255, blank=True)
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="permissions",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class Role(models.Model):
    SCOPE_CHOICES = [
        ("global", "Global"),
        ("tenant", "Tenant"),
        ("module", "Module"),
    ]

    code = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES, default="tenant")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.code


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="role_permissions"
    )

    class Meta:
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.code}:{self.permission.code}"


class TenantMembership(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("invited", "Invited"),
        ("suspended", "Suspended"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenant_memberships"
    )
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tenant")

    def __str__(self):
        return f"{self.user_id}:{self.tenant.tenant_code}"


class MembershipRole(models.Model):
    membership = models.ForeignKey(
        TenantMembership, on_delete=models.CASCADE, related_name="membership_roles"
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="membership_roles")
    module = models.ForeignKey(
        Module,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="membership_roles",
    )

    class Meta:
        unique_together = ("membership", "role", "module")

    def __str__(self):
        module_code = self.module.code if self.module else "all"
        return f"{self.membership_id}:{self.role.code}:{module_code}"


class UserTwoFactor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="two_factor",
    )
    secret = models.CharField(max_length=64, default="", blank=True)
    is_enabled = models.BooleanField(default=False)
    last_verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user_id"]

    def __str__(self):
        return f"2FA:{self.user_id}:{self.is_enabled}"


class UserTwoFactorBackupCode(models.Model):
    two_factor = models.ForeignKey(
        UserTwoFactor,
        on_delete=models.CASCADE,
        related_name="backup_codes",
    )
    code_hash = models.CharField(max_length=128, unique=True)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["two_factor", "is_used"]),
        ]

    def __str__(self):
        return f"2FA-Backup:{self.two_factor_id}:{self.is_used}"


class SensitiveAccessEvent(models.Model):
    STATUS_CHOICES = [
        ("granted", "Granted"),
        ("denied", "Denied"),
        ("challenge", "Challenge Required"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sensitive_access_events",
    )
    permission_code = models.CharField(max_length=120)
    path = models.CharField(max_length=255)
    ip_address = models.CharField(max_length=64, blank=True, default="")
    user_agent = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="granted")
    reason = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["permission_code", "created_at"]),
            models.Index(fields=["status", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.permission_code}:{self.status}"
