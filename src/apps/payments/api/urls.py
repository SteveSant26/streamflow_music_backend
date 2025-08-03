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
]
