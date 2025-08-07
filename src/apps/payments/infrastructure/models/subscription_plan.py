import uuid

from django.db import models

AMOUNT_HELP_TEXT = "Monto en centavos"


class SubscriptionPlanModel(models.Model):
    """Modelo para planes de suscripción"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.IntegerField(help_text=AMOUNT_HELP_TEXT)
    currency = models.CharField(max_length=3, default="EUR")
    interval = models.CharField(
        max_length=10, choices=[("month", "Mensual"), ("year", "Anual")]
    )
    interval_count = models.IntegerField(default=1)
    features = models.JSONField(default=list)
    stripe_price_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscription_plans"
        ordering = ["price"]

    def __str__(self):
        return f"{self.name} - {self.price/100:.2f} {self.currency}/{self.interval}"
