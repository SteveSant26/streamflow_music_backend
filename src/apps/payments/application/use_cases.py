"""
Use cases for payment domain
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..domain.entities import Invoice, PaymentMethod, Subscription, SubscriptionPlan
from ..domain.interfaces import (
    IInvoiceRepository,
    IPaymentMethodRepository,
    IPaymentRepository,
    IStripeService,
    ISubscriptionPlanRepository,
    ISubscriptionRepository,
)


@dataclass
class CreateCheckoutSessionRequest:
    user_id: str
    plan_id: str
    success_url: str
    cancel_url: str
    allow_promotion_codes: bool = True


@dataclass
class CreateBillingPortalRequest:
    user_id: str
    return_url: str


class GetSubscriptionPlansUseCase:
    """Caso de uso para obtener planes de suscripción"""

    def __init__(self, plan_repository: ISubscriptionPlanRepository):
        self.plan_repository = plan_repository

    async def execute(self) -> List[SubscriptionPlan]:
        """Obtiene todos los planes activos"""
        return await self.plan_repository.get_all_active()


class GetUserSubscriptionUseCase:
    """Caso de uso para obtener la suscripción de un usuario"""

    def __init__(self, subscription_repository: ISubscriptionRepository):
        self.subscription_repository = subscription_repository

    async def execute(self, user_id: str) -> Optional[Subscription]:
        """Obtiene la suscripción activa del usuario"""
        return await self.subscription_repository.get_by_user_id(user_id)


class CreateCheckoutSessionUseCase:
    """Caso de uso para crear una sesión de checkout"""

    def __init__(
        self,
        stripe_service: IStripeService,
        plan_repository: ISubscriptionPlanRepository,
        subscription_repository: ISubscriptionRepository,
    ):
        self.stripe_service = stripe_service
        self.plan_repository = plan_repository
        self.subscription_repository = subscription_repository

    async def execute(self, request: CreateCheckoutSessionRequest) -> Dict[str, Any]:
        """Crea una sesión de checkout en Stripe"""
        # Verificar que el plan existe
        plan = await self.plan_repository.get_by_id(request.plan_id)
        if not plan:
            raise ValueError(f"Plan {request.plan_id} no encontrado")

        # Verificar si el usuario ya tiene una suscripción activa
        existing_subscription = await self.subscription_repository.get_by_user_id(
            request.user_id
        )
        if existing_subscription and existing_subscription.is_active:
            # Si ya tiene suscripción, crear checkout para cambio de plan
            mode = "subscription"
            subscription_data = {
                "subscription": existing_subscription.stripe_subscription_id,
                "items": [{"price": plan.stripe_price_id, "quantity": 1}],
            }
        else:
            # Nueva suscripción
            mode = "subscription"
            subscription_data = {
                "items": [{"price": plan.stripe_price_id, "quantity": 1}]
            }

        # Obtener o crear customer ID de Stripe (esto debería venir del usuario)
        customer_id = f"customer_for_user_{request.user_id}"  # Placeholder

        # Crear sesión de checkout
        session = await self.stripe_service.create_checkout_session(
            customer_id=customer_id,
            price_id=plan.stripe_price_id,
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            allow_promotion_codes=request.allow_promotion_codes,
            mode=mode,
            **subscription_data,
        )

        return {"url": session.get("url"), "session_id": session.get("id")}


class CreateBillingPortalSessionUseCase:
    """Caso de uso para crear sesión del portal de facturación"""

    def __init__(
        self,
        stripe_service: IStripeService,
        subscription_repository: ISubscriptionRepository,
    ):
        self.stripe_service = stripe_service
        self.subscription_repository = subscription_repository

    async def execute(self, request: CreateBillingPortalRequest) -> Dict[str, Any]:
        """Crea una sesión del portal de facturación"""
        # Obtener la suscripción del usuario
        subscription = await self.subscription_repository.get_by_user_id(
            request.user_id
        )
        if not subscription:
            raise ValueError("Usuario no tiene suscripción activa")

        # Crear sesión del portal
        session = await self.stripe_service.create_billing_portal_session(
            customer_id=subscription.stripe_customer_id, return_url=request.return_url
        )

        return {"url": session.get("url")}


class CancelSubscriptionUseCase:
    """Caso de uso para cancelar una suscripción"""

    def __init__(
        self,
        stripe_service: IStripeService,
        subscription_repository: ISubscriptionRepository,
    ):
        self.stripe_service = stripe_service
        self.subscription_repository = subscription_repository

    async def execute(self, subscription_id: str) -> bool:
        """Cancela una suscripción"""
        # Obtener la suscripción
        subscription = await self.subscription_repository.get_by_stripe_subscription_id(
            subscription_id
        )
        if not subscription:
            raise ValueError("Suscripción no encontrada")

        # Cancelar en Stripe
        await self.stripe_service.cancel_subscription(
            subscription.stripe_subscription_id
        )

        # Actualizar en base de datos
        return await self.subscription_repository.cancel(subscription.id)


class GetPaymentMethodsUseCase:
    """Caso de uso para obtener métodos de pago de un usuario"""

    def __init__(self, payment_method_repository: IPaymentMethodRepository):
        self.payment_method_repository = payment_method_repository

    async def execute(self, user_id: str) -> List[PaymentMethod]:
        """Obtiene los métodos de pago del usuario"""
        return await self.payment_method_repository.get_by_user_id(user_id)


class GetUpcomingInvoiceUseCase:
    """Caso de uso para obtener la próxima factura"""

    def __init__(
        self,
        stripe_service: IStripeService,
        subscription_repository: ISubscriptionRepository,
    ):
        self.stripe_service = stripe_service
        self.subscription_repository = subscription_repository

    async def execute(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene la próxima factura del usuario"""
        # Obtener la suscripción del usuario
        subscription = await self.subscription_repository.get_by_user_id(user_id)
        if not subscription:
            return None

        # Obtener próxima factura de Stripe
        try:
            invoice = await self.stripe_service.get_upcoming_invoice(
                subscription.stripe_customer_id
            )
            return invoice
        except Exception:
            return None


class GetInvoiceHistoryUseCase:
    """Caso de uso para obtener historial de facturas"""

    def __init__(self, invoice_repository: IInvoiceRepository):
        self.invoice_repository = invoice_repository

    async def execute(self, user_id: str, limit: int = 10) -> List[Invoice]:
        """Obtiene el historial de facturas del usuario"""
        return await self.invoice_repository.get_by_user_id(user_id, limit)


class ProcessStripeWebhookUseCase:
    """Caso de uso para procesar webhooks de Stripe"""

    def __init__(
        self,
        stripe_service: IStripeService,
        subscription_repository: ISubscriptionRepository,
        invoice_repository: IInvoiceRepository,
        payment_repository: IPaymentRepository,
    ):
        self.stripe_service = stripe_service
        self.subscription_repository = subscription_repository
        self.invoice_repository = invoice_repository
        self.payment_repository = payment_repository

    async def execute(self, payload: bytes, signature: str) -> bool:
        """Procesa un evento de webhook de Stripe"""
        try:
            # Verificar y construir el evento
            event = self.stripe_service.construct_webhook_event(payload, signature)

            event_type = event.get("type")
            event_data = event.get("data", {}).get("object", {})

            # Procesar según el tipo de evento
            if event_type == "customer.subscription.created":
                await self._handle_subscription_created(event_data)
            elif event_type == "customer.subscription.updated":
                await self._handle_subscription_updated(event_data)
            elif event_type == "customer.subscription.deleted":
                await self._handle_subscription_deleted(event_data)
            elif event_type == "invoice.payment_succeeded":
                await self._handle_invoice_payment_succeeded(event_data)
            elif event_type == "invoice.payment_failed":
                await self._handle_invoice_payment_failed(event_data)

            return True

        except Exception as e:
            print(f"Error procesando webhook: {e}")
            return False

    async def _handle_subscription_created(self, subscription_data: Dict[str, Any]):
        """Maneja la creación de una suscripción"""
        # Implementar lógica para crear/actualizar suscripción en BD

    async def _handle_subscription_updated(self, subscription_data: Dict[str, Any]):
        """Maneja la actualización de una suscripción"""
        # Implementar lógica para actualizar suscripción en BD

    async def _handle_subscription_deleted(self, subscription_data: Dict[str, Any]):
        """Maneja la eliminación de una suscripción"""
        # Implementar lógica para cancelar suscripción en BD

    async def _handle_invoice_payment_succeeded(self, invoice_data: Dict[str, Any]):
        """Maneja el pago exitoso de una factura"""
        # Implementar lógica para registrar pago exitoso

    async def _handle_invoice_payment_failed(self, invoice_data: Dict[str, Any]):
        """Maneja el fallo de pago de una factura"""
        # Implementar lógica para manejar fallo de pago
