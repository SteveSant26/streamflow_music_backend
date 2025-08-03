"""
Custom exceptions for payment domain
"""


class PaymentError(Exception):
    """Base exception for payment errors"""


class StripeServiceError(PaymentError):
    """Exception for Stripe service errors"""


class CustomerCreationError(StripeServiceError):
    """Exception for customer creation errors"""


class CheckoutSessionError(StripeServiceError):
    """Exception for checkout session errors"""


class BillingPortalError(StripeServiceError):
    """Exception for billing portal errors"""


class SubscriptionError(StripeServiceError):
    """Exception for subscription errors"""


class PaymentMethodError(StripeServiceError):
    """Exception for payment method errors"""


class WebhookError(StripeServiceError):
    """Exception for webhook errors"""


class InvoiceError(StripeServiceError):
    """Exception for invoice errors"""


class PlanNotFoundError(PaymentError):
    """Exception when subscription plan is not found"""


class SubscriptionNotFoundError(PaymentError):
    """Exception when subscription is not found"""
