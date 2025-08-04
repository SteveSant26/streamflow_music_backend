"""
Repository interfaces for payment domain
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from .entities import (
    Invoice,
    Payment,
    PaymentMethod,
    StripeWebhookEvent,
    Subscription,
    SubscriptionPlan,
)


class ISubscriptionPlanRepository(ABC):
    """Interface para el repositorio de planes de suscripción"""

    @abstractmethod
    async def get_all_active(self) -> List[SubscriptionPlan]:
        """Obtiene todos los planes activos"""

    @abstractmethod
    async def get_by_id(self, plan_id: str) -> Optional[SubscriptionPlan]:
        """Obtiene un plan por ID"""

    @abstractmethod
    async def get_by_stripe_price_id(
        self, stripe_price_id: str
    ) -> Optional[SubscriptionPlan]:
        """Obtiene un plan por el price ID de Stripe"""

    @abstractmethod
    async def create(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        """Crea un nuevo plan"""

    @abstractmethod
    async def update(self, plan: SubscriptionPlan) -> SubscriptionPlan:
        """Actualiza un plan existente"""


class ISubscriptionRepository(ABC):
    """Interface para el repositorio de suscripciones"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Subscription]:
        """Obtiene la suscripción activa de un usuario"""

    @abstractmethod
    async def get_by_stripe_subscription_id(
        self, stripe_subscription_id: str
    ) -> Optional[Subscription]:
        """Obtiene una suscripción por su ID de Stripe"""

    @abstractmethod
    async def create(self, subscription: Subscription) -> Subscription:
        """Crea una nueva suscripción"""

    @abstractmethod
    async def update(self, subscription: Subscription) -> Subscription:
        """Actualiza una suscripción existente"""

    @abstractmethod
    async def cancel(self, subscription_id: str) -> bool:
        """Cancela una suscripción"""


class IPaymentMethodRepository(ABC):
    """Interface para el repositorio de métodos de pago"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[PaymentMethod]:
        """Obtiene todos los métodos de pago de un usuario"""

    @abstractmethod
    async def get_default_by_user_id(self, user_id: str) -> Optional[PaymentMethod]:
        """Obtiene el método de pago por defecto de un usuario"""

    @abstractmethod
    async def create(self, payment_method: PaymentMethod) -> PaymentMethod:
        """Crea un nuevo método de pago"""

    @abstractmethod
    async def update(self, payment_method: PaymentMethod) -> PaymentMethod:
        """Actualiza un método de pago"""

    @abstractmethod
    async def delete(self, payment_method_id: str) -> bool:
        """Elimina un método de pago"""


class IInvoiceRepository(ABC):
    """Interface para el repositorio de facturas"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Invoice]:
        """Obtiene las facturas de un usuario"""

    @abstractmethod
    async def get_by_stripe_invoice_id(
        self, stripe_invoice_id: str
    ) -> Optional[Invoice]:
        """Obtiene una factura por su ID de Stripe"""

    @abstractmethod
    async def create(self, invoice: Invoice) -> Invoice:
        """Crea una nueva factura"""

    @abstractmethod
    async def update(self, invoice: Invoice) -> Invoice:
        """Actualiza una factura"""


class IPaymentRepository(ABC):
    """Interface para el repositorio de pagos"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Payment]:
        """Obtiene los pagos de un usuario"""

    @abstractmethod
    async def get_by_stripe_payment_intent_id(
        self, stripe_payment_intent_id: str
    ) -> Optional[Payment]:
        """Obtiene un pago por su Payment Intent ID de Stripe"""

    @abstractmethod
    async def create(self, payment: Payment) -> Payment:
        """Crea un nuevo pago"""

    @abstractmethod
    async def update(self, payment: Payment) -> Payment:
        """Actualiza un pago"""


class IStripeWebhookRepository(ABC):
    """Interface para el repositorio de webhooks de Stripe"""

    @abstractmethod
    async def get_by_stripe_event_id(
        self, stripe_event_id: str
    ) -> Optional[StripeWebhookEvent]:
        """Obtiene un evento por su ID de Stripe"""

    @abstractmethod
    async def create(self, webhook_event: StripeWebhookEvent) -> StripeWebhookEvent:
        """Crea un nuevo evento de webhook"""

    @abstractmethod
    async def mark_as_processed(self, event_id: str) -> bool:
        """Marca un evento como procesado"""


class IStripeService(ABC):
    """Interface para el servicio de Stripe"""

    @abstractmethod
    async def create_customer(self, user_id: str, email: str, name: str) -> str:
        """Crea un cliente en Stripe"""

    @abstractmethod
    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """Crea una sesión de checkout"""

    @abstractmethod
    async def create_billing_portal_session(
        self, customer_id: str, return_url: str
    ) -> Dict[str, Any]:
        """Crea una sesión del portal de facturación"""

    @abstractmethod
    async def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Obtiene una suscripción de Stripe"""

    @abstractmethod
    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any] | None:
        """Cancela una suscripción en Stripe"""

    @abstractmethod
    async def get_upcoming_invoice(self, customer_id: str) -> Dict[str, Any] | None:
        """Obtiene la próxima factura de un cliente"""

    @abstractmethod
    async def get_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Obtiene los métodos de pago de un cliente"""

    @abstractmethod
    def construct_webhook_event(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Construye un evento de webhook desde el payload"""
