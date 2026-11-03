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
        post_save.connect(queue_resource, sender="fleet.Vehicle", dispatch_uid="central-sync-resource-save")
        post_delete.connect(queue_resource, sender="fleet.Vehicle", dispatch_uid="central-sync-resource-delete")
        from .inventory import queue_related
        post_save.connect(queue_related, sender="fleet.VehicleBrand", dispatch_uid="central-related-fleet.VehicleBrand")
        post_save.connect(queue_related, sender="fleet.VehicleModel", dispatch_uid="central-related-fleet.VehicleModel")
        post_save.connect(queue_related, sender="settings_app.BusinessProfile", dispatch_uid="central-related-settings_app.BusinessProfile")
