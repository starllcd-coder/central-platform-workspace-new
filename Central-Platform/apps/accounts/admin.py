from django.contrib import admin
from django.contrib import messages

from .models import (
    MembershipRole,
    Permission,
    Role,
    RolePermission,
    TenantMembership,
    UserTwoFactor,
    UserTwoFactorBackupCode,
    SensitiveAccessEvent,
)
from .twofa import backup_code_hash, generate_backup_codes, generate_base32_secret

admin.site.register(Permission)
admin.site.register(Role)
admin.site.register(RolePermission)
admin.site.register(TenantMembership)
admin.site.register(MembershipRole)


@admin.register(UserTwoFactor)
class UserTwoFactorAdmin(admin.ModelAdmin):
    list_display = ("user", "is_enabled", "last_verified_at", "updated_at")
    search_fields = ("user__username", "user__email")
    actions = ("force_reset_two_factor", "regenerate_backup_codes")

    @admin.action(description="Force reset selected users' 2FA")
    def force_reset_two_factor(self, request, queryset):
        updated = 0
        for row in queryset:
            row.secret = generate_base32_secret()
            row.is_enabled = False
            row.last_verified_at = None
            row.save(update_fields=["secret", "is_enabled", "last_verified_at", "updated_at"])
            UserTwoFactorBackupCode.objects.filter(two_factor=row).delete()
            updated += 1
        self.message_user(request, f"2FA reset for {updated} user(s).", level=messages.WARNING)

    @admin.action(description="Regenerate backup codes for selected users")
    def regenerate_backup_codes(self, request, queryset):
        updated = 0
        for row in queryset:
            if not row.is_enabled:
                continue
            codes = generate_backup_codes()
            UserTwoFactorBackupCode.objects.filter(two_factor=row).delete()
            UserTwoFactorBackupCode.objects.bulk_create(
                [UserTwoFactorBackupCode(two_factor=row, code_hash=backup_code_hash(item)) for item in codes]
            )
            updated += 1
        self.message_user(
            request,
            f"Backup codes regenerated for {updated} enabled user(s).",
            level=messages.SUCCESS,
        )


@admin.register(UserTwoFactorBackupCode)
class UserTwoFactorBackupCodeAdmin(admin.ModelAdmin):
    list_display = ("two_factor", "is_used", "used_at", "created_at")
    list_filter = ("is_used",)


@admin.register(SensitiveAccessEvent)
class SensitiveAccessEventAdmin(admin.ModelAdmin):
    list_display = ("user", "permission_code", "status", "ip_address", "created_at")
    list_filter = ("status", "permission_code")
    search_fields = ("user__username", "permission_code", "path", "ip_address")
