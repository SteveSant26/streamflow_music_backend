"""
Use case for getting upcoming invoice
"""

from typing import Any, Dict, Optional

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.interfaces.stripe_service import IStripeService
from ..domain.repository import ISubscriptionRepository


class GetUpcomingInvoiceUseCase(BaseUseCase[str, Optional[Dict[str, Any]]]):
    """Caso de uso para obtener la próxima factura"""

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
    async def execute(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene la próxima factura del usuario"""
        # Obtener la suscripción del usuario
        subscription = await self.subscription_repository.get_by_user_id(user_id)
        if not subscription:
            return None

        # Obtener próxima factura de Stripe
        try:
            invoice = self.stripe_service.get_upcoming_invoice(
                subscription.stripe_customer_id
            )
            return invoice
        except Exception:
            return None
