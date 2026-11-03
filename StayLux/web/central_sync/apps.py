from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save, post_delete

class CentralSyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "central_sync"

    def ready(self):
        from .signals import queue_status
        post_save.connect(queue_status, sender="bookings.Booking", dispatch_uid="central-sync-status-save")
        post_delete.connect(queue_status, sender="bookings.Booking", dispatch_uid="central-sync-status-delete")
        from .inventory import queue_resource
        post_save.connect(queue_resource, sender="inventory.Unit", dispatch_uid="central-sync-resource-save")
        post_delete.connect(queue_resource, sender="inventory.Unit", dispatch_uid="central-sync-resource-delete")
        from .inventory import queue_related
        post_save.connect(queue_related, sender="inventory.UnitType", dispatch_uid="central-related-inventory.UnitType")
        post_save.connect(queue_related, sender="settings_app.PropertyProfile", dispatch_uid="central-related-settings_app.PropertyProfile")
        post_save.connect(queue_related, sender="pricing.RatePlan", dispatch_uid="central-related-pricing.RatePlan")
        post_save.connect(queue_related, sender="pricing.SeasonalRateRule", dispatch_uid="central-related-pricing.SeasonalRateRule")
