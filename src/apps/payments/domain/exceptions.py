"""
Custom exceptions for payment domain
"""


class PaymentError(Exception):
    """Base exception for payment errors"""
    pass


class StripeServiceError(PaymentError):
    """Exception for Stripe service errors"""
    pass


class CustomerCreationError(StripeServiceError):
    """Exception for customer creation errors"""
    pass


class CheckoutSessionError(StripeServiceError):
    """Exception for checkout session errors"""
    pass


class BillingPortalError(StripeServiceError):
    """Exception for billing portal errors"""
    pass


class SubscriptionError(StripeServiceError):
    """Exception for subscription errors"""
    pass


class PaymentMethodError(StripeServiceError):
    """Exception for payment method errors"""
    pass


class WebhookError(StripeServiceError):
    """Exception for webhook errors"""
    pass


class InvoiceError(StripeServiceError):
    """Exception for invoice errors"""
    pass


class PlanNotFoundError(PaymentError):
    """Exception when subscription plan is not found"""
    pass


class SubscriptionNotFoundError(PaymentError):
    """Exception when subscription is not found"""
    pass
