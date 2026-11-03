from django.db import models

class Delivery(models.Model):
    external_id = models.CharField(max_length=80, unique=True)
    payload_hash = models.CharField(max_length=64)
    booking_id = models.PositiveBigIntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RequestNonce(models.Model):
    nonce = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
