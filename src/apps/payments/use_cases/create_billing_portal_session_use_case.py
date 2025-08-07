"""
Use case for creating billing portal session
"""

from dataclasses import dataclass
from typing import Any, Dict

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.interfaces.stripe_service import IStripeService
from ..domain.repository import ISubscriptionRepository


@dataclass
class CreateBillingPortalRequest:
    user_id: str
    return_url: str


class CreateBillingPortalSessionUseCase(
    BaseUseCase[CreateBillingPortalRequest, Dict[str, Any]]
):
    """Caso de uso para crear sesión del portal de facturación"""

    def __init__(
        self,
        stripe_service: IStripeService,
        subscription_repository: ISubscriptionRepository,
    ):
        super().__init__()
        self.stripe_service = stripe_service
        self.subscription_repository = subscription_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
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
