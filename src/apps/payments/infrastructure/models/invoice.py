import uuid

from django.db import models

from .subscription import SubscriptionModel

AMOUNT_HELP_TEXT = "Monto en centavos"


class InvoiceModel(models.Model):
    """Modelo para facturas"""

    STATUS_CHOICES = [
        ("draft", "Borrador"),
        ("open", "Abierta"),
        ("paid", "Pagada"),
        ("uncollectible", "Incobrable"),
        ("void", "Anulada"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_profile = models.ForeignKey(
        "user_profile.UserProfile",
        on_delete=models.CASCADE,
        related_name="invoices",
    )
    subscription = models.ForeignKey(
        SubscriptionModel,
        on_delete=models.CASCADE,
        related_name="invoices",
        null=True,
        blank=True,
    )
    stripe_invoice_id = models.CharField(max_length=100, unique=True)
    amount = models.IntegerField(help_text=AMOUNT_HELP_TEXT)
    currency = models.CharField(max_length=3, default="EUR")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    due_date = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "invoices"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Factura {self.stripe_invoice_id} - {self.amount/100:.2f} {self.currency}"
        )
