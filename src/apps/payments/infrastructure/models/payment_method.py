import uuid

from django.db import models


class PaymentMethodModel(models.Model):
    """Modelo para métodos de pago"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user_profile = models.ForeignKey(
        "user_profile.UserProfileModel",
        on_delete=models.CASCADE,
        related_name="payment_methods",
    )

    stripe_payment_method_id = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=20)
    card_brand = models.CharField(max_length=20, blank=True, default="")
    card_last4 = models.CharField(max_length=4, blank=True, default="")
    card_exp_month = models.IntegerField(null=True, blank=True)
    card_exp_year = models.IntegerField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_methods"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        if self.card_brand and self.card_last4:
            return f"{self.card_brand} ****{self.card_last4}"
        return f"{self.type} - {self.user_profile.email}"
