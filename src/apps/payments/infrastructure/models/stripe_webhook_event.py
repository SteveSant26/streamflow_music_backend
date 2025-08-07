import uuid

from django.db import models


class StripeWebhookEventModel(models.Model):
    """Modelo para eventos de webhook"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stripe_event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=50)
    processed = models.BooleanField(default=False)
    data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "stripe_webhook_events"
        ordering = ["-created_at"]

    def __str__(self):
        status = "Procesado" if self.processed else "Pendiente"
        return f"{self.event_type} - {status}"
