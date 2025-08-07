<<<<<<< HEAD
from typing import List

from django.urls import URLPattern

# from ..presentation.views import (
#     BillingPortalSessionView,
#     CancelSubscriptionView,
#     CheckoutSessionView,
#     GetInvoicesView,
#     GetPaymentHistoryView,
#     GetSubscriptionPlansView,
#     GetUserSubscriptionsView,
#     ProcessPaymentView,
#     StripeWebhookView,
# )

# Temporary empty URL patterns for migrations
urlpatterns: List[URLPattern] = [
    # path("subscription-plans/", GetSubscriptionPlansView.as_view(), name="subscription-plans"),
    # path("checkout-session/", CheckoutSessionView.as_view(), name="checkout-session"),
    # path("stripe-webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    # path("subscriptions/", GetUserSubscriptionsView.as_view(), name="user-subscriptions"),
    # path("cancel-subscription/", CancelSubscriptionView.as_view(), name="cancel-subscription"),
    # path("payment-history/", GetPaymentHistoryView.as_view(), name="payment-history"),
    # path("billing-portal/", BillingPortalSessionView.as_view(), name="billing-portal"),
    # path("process-payment/", ProcessPaymentView.as_view(), name="process-payment"),
    # path("invoices/", GetInvoicesView.as_view(), name="invoices"),
=======
from django.urls import path

from .views import (
    StripeWebhookView,
    cancel_subscription,
    create_billing_portal_session,
    create_checkout_session,
    get_invoice_history,
    get_payment_methods,
    get_stripe_public_key,
    get_subscription_plans,
    get_upcoming_invoice,
    get_user_subscription,
)

app_name = "payments"

urlpatterns = [
    # Planes de suscripción
    path("plans/", get_subscription_plans, name="subscription-plans"),
    # Suscripciones
    path("subscription/", get_user_subscription, name="user-subscription"),
    path("subscription/checkout/", create_checkout_session, name="create-checkout"),
    path("subscription/portal/", create_billing_portal_session, name="billing-portal"),
    path("subscription/cancel/", cancel_subscription, name="cancel-subscription"),
    # Métodos de pago
    path("payment-methods/", get_payment_methods, name="payment-methods"),
    # Facturas
    path("invoices/upcoming/", get_upcoming_invoice, name="upcoming-invoice"),
    path("invoices/history/", get_invoice_history, name="invoice-history"),
    # Configuración
    path("config/stripe-key/", get_stripe_public_key, name="stripe-public-key"),
    # Webhooks
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
]
