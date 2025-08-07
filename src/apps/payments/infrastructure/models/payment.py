import uuid

from django.db import models

from .invoice import InvoiceModel
from .payment_method import PaymentMethodModel

AMOUNT_HELP_TEXT = "Monto en centavos"


class PaymentModel(models.Model):
    """Modelo para pagos"""

    STATUS_CHOICES = [
        ("succeeded", "Exitoso"),
        ("pending", "Pendiente"),
        ("failed", "Fallido"),
        ("canceled", "Cancelado"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(
        "user_profile.UserProfile",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    stripe_payment_intent_id = models.CharField(max_length=100, unique=True)
    invoice = models.ForeignKey(
        InvoiceModel,
        on_delete=models.SET_NULL,
        related_name="payments",
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        PaymentMethodModel,
        on_delete=models.SET_NULL,
        related_name="payments",
        null=True,
        blank=True,
    )
    amount = models.IntegerField(help_text=AMOUNT_HELP_TEXT)
    currency = models.CharField(max_length=3, default="EUR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pago {self.stripe_payment_intent_id} - {self.amount/100:.2f} {self.currency}"
