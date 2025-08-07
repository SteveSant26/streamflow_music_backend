"""
Use case for canceling subscription
"""

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.interfaces.stripe_service import IStripeService
from ..domain.repository import ISubscriptionRepository


class CancelSubscriptionUseCase(BaseUseCase[str, bool]):
    """Caso de uso para cancelar una suscripción"""

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
