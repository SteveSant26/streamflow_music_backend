"""
Django models for payments app
"""
import uuid

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

# Constants
AMOUNT_HELP_TEXT = "Monto en centavos"


class SubscriptionPlan(models.Model):
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


class Subscription(models.Model):
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
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
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
        return f"{self.user.email} - {self.plan.name} ({self.status})"

    @property
    def is_active(self):
        return self.status == "active"

    @property
    def is_on_trial(self):
        from django.utils import timezone

        if not self.trial_end:
            return False
        return self.trial_end > timezone.now()


class PaymentMethod(models.Model):
    """Modelo para métodos de pago"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_methods"
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
        return f"{self.type} - {self.user.email}"


class Invoice(models.Model):
    """Modelo para facturas"""

    STATUS_CHOICES = [
        ("draft", "Borrador"),
        ("open", "Abierta"),
        ("paid", "Pagada"),
        ("uncollectible", "Incobrable"),
        ("void", "Anulada"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    subscription = models.ForeignKey(
        Subscription,
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


class Payment(models.Model):
    """Modelo para pagos"""

    STATUS_CHOICES = [
        ("succeeded", "Exitoso"),
        ("pending", "Pendiente"),
        ("failed", "Fallido"),
        ("canceled", "Cancelado"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    stripe_payment_intent_id = models.CharField(max_length=100, unique=True)
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.SET_NULL,
        related_name="payments",
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        PaymentMethod,
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


class StripeWebhookEvent(models.Model):
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


class CheckoutSession(models.Model):
    """Modelo para sesiones de checkout"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="checkout_sessions"
    )
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
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


class BillingPortalSession(models.Model):
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
