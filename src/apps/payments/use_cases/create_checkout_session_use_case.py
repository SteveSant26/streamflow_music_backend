"""
Use case for creating checkout session
"""

from dataclasses import dataclass
from typing import Any, Dict

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.interfaces.stripe_service import IStripeService
from ..domain.repository import ISubscriptionPlanRepository, ISubscriptionRepository


@dataclass
class CreateCheckoutSessionRequest:
    user_id: str
    plan_id: str
    success_url: str
    cancel_url: str
    allow_promotion_codes: bool = True


class CreateCheckoutSessionUseCase(
    BaseUseCase[CreateCheckoutSessionRequest, Dict[str, Any]]
):
    """Caso de uso para crear una sesión de checkout"""

    def __init__(
        self,
        stripe_service: IStripeService,
        plan_repository: ISubscriptionPlanRepository,
        subscription_repository: ISubscriptionRepository,
    ):
        super().__init__()
        self.stripe_service = stripe_service
        self.plan_repository = plan_repository
        self.subscription_repository = subscription_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
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
