import uuid

from django.db import models

from .subscription_plan import SubscriptionPlanModel


class SubscriptionModel(models.Model):
    """Modelo para suscripciones de usuarios"""

    STATUS_CHOICES = [
        ("active", "Activa"),
        ("canceled", "Cancelada"),
        ("incomplete", "Incompleta"),
        ("incomplete_expired", "Incompleta Expirada"),
        ("past_due", "Vencida"),
        ("unpaid", "Sin Pagar"),
        ("trialing", "En Prueba"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(
        "user_profile.UserProfile",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(SubscriptionPlanModel, on_delete=models.PROTECT)
    stripe_subscription_id = models.CharField(max_length=100, unique=True)
    stripe_customer_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    trial_start = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "subscriptions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_profile.email} - {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def is_on_trial(self):
        from django.utils import timezone

        if not self.trial_end:
            return False
        return self.trial_end > timezone.now()
