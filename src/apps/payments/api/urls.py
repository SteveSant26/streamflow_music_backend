from django.urls import path

from .views import (
    CancelSubscriptionAPIView,
    CreateBillingPortalSessionAPIView,
    CreateCheckoutSessionAPIView,
    GetInvoiceHistoryAPIView,
    GetPaymentMethodsAPIView,
    GetStripePublicKeyAPIView,
    GetSubscriptionPlansAPIView,
    GetUpcomingInvoiceAPIView,
    GetUserSubscriptionAPIView,
    StripeWebhookView,
)

app_name = "payments"

urlpatterns = [
    # Planes de suscripción
    path("plans/", GetSubscriptionPlansAPIView.as_view(), name="subscription-plans"),
    # Suscripciones
    path(
        "subscription/", GetUserSubscriptionAPIView.as_view(), name="user-subscription"
    ),
    path(
        "subscription/checkout/",
        CreateCheckoutSessionAPIView.as_view(),
        name="create-checkout",
    ),
    path(
        "subscription/portal/",
        CreateBillingPortalSessionAPIView.as_view(),
        name="billing-portal",
    ),
    path(
        "subscription/cancel/",
        CancelSubscriptionAPIView.as_view(),
        name="cancel-subscription",
    ),
    # Métodos de pago
    path(
        "payment-methods/", GetPaymentMethodsAPIView.as_view(), name="payment-methods"
    ),
    # Facturas
    path(
        "invoices/upcoming/",
        GetUpcomingInvoiceAPIView.as_view(),
        name="upcoming-invoice",
    ),
    path(
        "invoices/history/", GetInvoiceHistoryAPIView.as_view(), name="invoice-history"
    ),
    # Configuración
    path(
        "config/stripe-key/",
        GetStripePublicKeyAPIView.as_view(),
        name="stripe-public-key",
    ),
    # Webhooks
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
