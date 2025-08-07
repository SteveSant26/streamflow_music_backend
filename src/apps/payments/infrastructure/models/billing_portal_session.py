import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class BillingPortalSessionModel(models.Model):
    """Modelo para sesiones del portal de facturación"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="billing_sessions"
    )
    stripe_session_id = models.CharField(max_length=100, unique=True)
    url = models.URLField()
    return_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "billing_portal_sessions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Portal {self.stripe_session_id} - {self.user.email}"
