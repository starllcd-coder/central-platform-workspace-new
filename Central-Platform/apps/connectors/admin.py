from django.contrib import admin

from .models import AppConnector, ConnectorEvent, ConnectorHealthLog, ConnectorRequestNonce

admin.site.register(AppConnector)
admin.site.register(ConnectorEvent)
admin.site.register(ConnectorRequestNonce)
admin.site.register(ConnectorHealthLog)
