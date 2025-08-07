from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PaymentResponseDTO:
    """DTO para las respuestas de pagos."""

    id: str
    user_id: str
    stripe_payment_intent_id: str
    amount: int
    currency: str
    status: str
    payment_method_id: Optional[str] = None
    invoice_id: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class CreatePaymentRequestDTO:
    """DTO para la request de creación de pago."""

    user_id: str
    amount: int
    currency: str
    payment_method_id: Optional[str] = None


@dataclass
class SubscriptionResponseDTO:
    """DTO para las respuestas de suscripciones."""

    id: str
    user_id: str
    plan_id: str
    stripe_subscription_id: str
    stripe_customer_id: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


@dataclass
class CreateSubscriptionRequestDTO:
    """DTO para la request de creación de suscripción."""

    user_id: str
    plan_id: str
    payment_method_id: Optional[str] = None


@dataclass
class SubscriptionPlanResponseDTO:
    """DTO para las respuestas de planes de suscripción."""

    id: str
    name: str
    description: str
    price: int
    currency: str
    interval: str
    interval_count: int
    features: list[str]
    stripe_price_id: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class InvoiceResponseDTO:
    """DTO para las respuestas de facturas."""

    id: str
    stripe_invoice_id: str
    subscription_id: str
    user_id: str
    amount: int
    currency: str
    status: str
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class PaymentMethodResponseDTO:
    """DTO para las respuestas de métodos de pago."""

    id: str
    user_id: str
    stripe_payment_method_id: str
    type: str
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    is_default: bool = False
    created_at: Optional[datetime] = None


@dataclass
class CreatePaymentMethodRequestDTO:
    """DTO para la request de creación de método de pago."""

    user_id: str
    stripe_payment_method_id: str
    type: str
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None


@dataclass
class StripeWebhookEventResponseDTO:
    """DTO para las respuestas de eventos de webhook de Stripe."""

    id: str
    stripe_event_id: str
    event_type: str
    processed: bool
    data: dict
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
