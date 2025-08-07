"""
Use case for getting user subscription
"""

from typing import Optional

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import SubscriptionEntity
from ..domain.repository import ISubscriptionRepository


class GetUserSubscriptionUseCase(BaseUseCase[str, Optional[SubscriptionEntity]]):
    """Caso de uso para obtener la suscripción de un usuario"""

    def __init__(self, subscription_repository: ISubscriptionRepository):
        super().__init__()
        self.subscription_repository = subscription_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, user_id: str) -> Optional[SubscriptionEntity]:
        """Obtiene la suscripción activa del usuario"""
        return await self.subscription_repository.get_by_user_id(user_id)
