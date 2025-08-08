from abc import ABC, abstractmethod
from typing import Any, Dict, List


class IStripeService(ABC):
    """Interface para el servicio de Stripe"""

    @abstractmethod
    def create_customer(self, user_profile_id: str, email: str, name: str) -> str:
        """Crea un cliente en Stripe"""

    @abstractmethod
    def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Crea una sesión de checkout"""

    @abstractmethod
    def create_billing_portal_session(
        self, customer_id: str, return_url: str
    ) -> Dict[str, Any]:
        """Crea una sesión del portal de facturación"""

    @abstractmethod
    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        """Obtiene una suscripción de Stripe"""

    @abstractmethod
    def cancel_subscription(self, subscription_id: str) -> Dict[str, Any] | None:
        """Cancela una suscripción en Stripe"""

    @abstractmethod
    def get_upcoming_invoice(self, customer_id: str) -> Dict[str, Any] | None:
        """Obtiene la próxima factura de un cliente"""

    @abstractmethod
    def get_payment_methods(self, customer_id: str) -> List[Dict[str, Any]]:
        """Obtiene los métodos de pago de un cliente"""

    @abstractmethod
    def construct_webhook_event(self, payload: bytes, signature: str) -> Dict[str, Any]:
        """Construye un evento de webhook desde el payload"""
