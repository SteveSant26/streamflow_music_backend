import uuid

from django.contrib.auth import get_user_model
from django.db import models

from .subscription_plan import SubscriptionPlanModel

User = get_user_model()
AMOUNT_HELP_TEXT = "Monto en centavos"


class CheckoutSessionModel(models.Model):
    """Modelo para sesiones de checkout"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="checkout_sessions"
    )
    plan = models.ForeignKey(SubscriptionPlanModel, on_delete=models.CASCADE)
    stripe_session_id = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField(help_text=AMOUNT_HELP_TEXT)
    currency = models.CharField(max_length=3, default="EUR")
    success_url = models.URLField()
    cancel_url = models.URLField()
    status = models.CharField(max_length=20, default="open")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "checkout_sessions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Checkout {self.stripe_session_id} - {self.user.email}"
