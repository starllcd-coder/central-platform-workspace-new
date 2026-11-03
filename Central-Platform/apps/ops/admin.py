from django.contrib import admin

from .models import AuditLog, NotificationEvent, NotificationTemplate, OccupancySnapshot

admin.site.register(AuditLog)
admin.site.register(NotificationTemplate)
admin.site.register(NotificationEvent)
admin.site.register(OccupancySnapshot)
