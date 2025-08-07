"""
Django admin conf    readonly_fields = ["id", "created_at", "updated_at"]

    @admin.display(description="Precio")
    def price_display(self, obj):
        return f"{obj.price/100:.2f} {obj.currency}"ion for payments
"""
<<<<<<< HEAD

=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from django.contrib import admin

from .infrastructure.models import (
    BillingPortalSession,
    CheckoutSession,
    Invoice,
    Payment,
    PaymentMethod,
    StripeWebhookEvent,
    Subscription,
    SubscriptionPlan,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price_display", "interval", "is_active", "created_at"]
    list_filter = ["interval", "is_active", "currency"]
    search_fields = ["name", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]

    @admin.display(description="Precio")
    def price_display(self, obj):
        return f"{obj.price/100:.2f} {obj.currency}"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "current_period_end", "is_active"]
    list_filter = ["status", "plan", "created_at"]
    search_fields = ["user__email", "stripe_subscription_id", "stripe_customer_id"]
    readonly_fields = [
        "id",
        "stripe_subscription_id",
        "stripe_customer_id",
        "created_at",
        "updated_at",
    ]
    raw_id_fields = ["user"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "card_display", "is_default", "created_at"]
    list_filter = ["type", "card_brand", "is_default"]
    search_fields = ["user__email", "stripe_payment_method_id"]
    readonly_fields = ["id", "stripe_payment_method_id", "created_at"]
    raw_id_fields = ["user"]

    @admin.display(description="Tarjeta")
    def card_display(self, obj):
        if obj.card_brand and obj.card_last4:
            return f"{obj.card_brand} ****{obj.card_last4}"
        return obj.type


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "stripe_invoice_id",
        "user",
        "amount_display",
        "status",
        "paid_at",
        "created_at",
    ]
    list_filter = ["status", "currency", "created_at"]
    search_fields = ["user__email", "stripe_invoice_id"]
    readonly_fields = ["id", "stripe_invoice_id", "created_at"]
    raw_id_fields = ["user", "subscription"]

    @admin.display(description="Monto")
    def amount_display(self, obj):
        return f"{obj.amount/100:.2f} {obj.currency}"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "stripe_payment_intent_id",
        "user",
        "amount_display",
        "status",
        "created_at",
    ]
    list_filter = ["status", "currency", "created_at"]
    search_fields = ["user__email", "stripe_payment_intent_id"]
    readonly_fields = ["id", "stripe_payment_intent_id", "created_at"]
    raw_id_fields = ["user", "invoice", "payment_method"]

    @admin.display(description="Monto")
    def amount_display(self, obj):
        return f"{obj.amount/100:.2f} {obj.currency}"


@admin.register(StripeWebhookEvent)
class StripeWebhookEventAdmin(admin.ModelAdmin):
    list_display = ["stripe_event_id", "event_type", "processed", "created_at"]
    list_filter = ["event_type", "processed", "created_at"]
    search_fields = ["stripe_event_id", "event_type"]
    readonly_fields = ["id", "stripe_event_id", "created_at", "processed_at"]

    def has_add_permission(self, request):
        return False


@admin.register(CheckoutSession)
class CheckoutSessionAdmin(admin.ModelAdmin):
    list_display = [
        "stripe_session_id",
        "user",
        "plan",
        "amount_display",
        "status",
        "created_at",
    ]
    list_filter = ["status", "currency", "created_at"]
    search_fields = ["user__email", "stripe_session_id"]
    readonly_fields = ["id", "stripe_session_id", "created_at"]
    raw_id_fields = ["user", "plan"]

    @admin.display(description="Monto")
    def amount_display(self, obj):
        return f"{obj.amount/100:.2f} {obj.currency}"


@admin.register(BillingPortalSession)
class BillingPortalSessionAdmin(admin.ModelAdmin):
    list_display = ["stripe_session_id", "user", "created_at", "expires_at"]
    list_filter = ["created_at"]
    search_fields = ["user__email", "stripe_session_id"]
    readonly_fields = ["id", "stripe_session_id", "url", "created_at"]
    raw_id_fields = ["user"]
