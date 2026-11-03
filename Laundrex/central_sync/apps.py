from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_save, post_delete

class CentralSyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "central_sync"

    def ready(self):
        from .signals import queue_status
        post_save.connect(queue_status, sender="orders.Order", dispatch_uid="central-sync-status-save")
        post_delete.connect(queue_status, sender="orders.Order", dispatch_uid="central-sync-status-delete")
        from .inventory import queue_resource
        post_save.connect(queue_resource, sender="catalog.ItemServicePrice", dispatch_uid="central-sync-resource-save")
        post_delete.connect(queue_resource, sender="catalog.ItemServicePrice", dispatch_uid="central-sync-resource-delete")
        from .inventory import queue_related
        post_save.connect(queue_related, sender="catalog.Service", dispatch_uid="central-related-catalog.Service")
        post_save.connect(queue_related, sender="catalog.Item", dispatch_uid="central-related-catalog.Item")
        post_save.connect(queue_related, sender="catalog.BranchItemServicePrice", dispatch_uid="central-related-branch-price")
