"""
Domain entities for payment system
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum


class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"


class PaymentStatus(Enum):
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    FAILED = "failed"
    CANCELED = "canceled"


class InvoiceStatus(Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    UNCOLLECTIBLE = "uncollectible"
    VOID = "void"


@dataclass
class SubscriptionPlan:
    """Plan de suscripción"""
    id: str
    name: str
    description: str
    price: int  # En centavos
    currency: str
    interval: str  # 'month' o 'year'
    interval_count: int
    features: List[str]
    stripe_price_id: str
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PaymentMethod:
    """Método de pago del usuario"""
    id: str
    stripe_payment_method_id: str
    user_id: str
    type: str  # 'card', 'sepa_debit', etc.
    card_brand: Optional[str] = None
    card_last4: Optional[str] = None
    card_exp_month: Optional[int] = None
    card_exp_year: Optional[int] = None
    is_default: bool = False
    created_at: Optional[datetime] = None


@dataclass
class Subscription:
    """Suscripción de usuario"""
    id: str
    user_id: str
    stripe_subscription_id: str
    stripe_customer_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    trial_start: Optional[datetime] = None
    trial_end: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        return self.status == SubscriptionStatus.ACTIVE

    @property
    def is_on_trial(self) -> bool:
        if not self.trial_end:
            return False
        return self.trial_end > datetime.now(timezone.utc)


@dataclass
class Invoice:
    """Factura de suscripción"""
    id: str
    stripe_invoice_id: str
    subscription_id: str
    user_id: str
    amount: int  # En centavos
    currency: str
    status: InvoiceStatus
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class Payment:
    """Pago realizado"""
    id: str
    stripe_payment_intent_id: str
    user_id: str
    amount: int  # En centavos
    currency: str
    status: PaymentStatus
    payment_method_id: Optional[str] = None
    invoice_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None


@dataclass
class StripeWebhookEvent:
    """Evento de webhook de Stripe"""
    id: str
    stripe_event_id: str
    event_type: str
    processed: bool = False
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None


@dataclass
class CheckoutSession:
    """Sesión de checkout de Stripe"""
    id: str
    stripe_session_id: str
    user_id: str
    plan_id: str
    amount: int
    currency: str
    success_url: str
    cancel_url: str
    status: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None


@dataclass
class BillingPortalSession:
    """Sesión del portal de facturación"""
    id: str
    stripe_session_id: str
    user_id: str
    url: str
    return_url: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
