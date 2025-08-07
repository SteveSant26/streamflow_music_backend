"""
Use case for getting subscription plans
"""

from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import SubscriptionPlan
from ..domain.repository import ISubscriptionPlanRepository


class GetSubscriptionPlansUseCase(BaseUseCase[None, List[SubscriptionPlan]]):
    """Caso de uso para obtener planes de suscripción"""

    def __init__(self, plan_repository: ISubscriptionPlanRepository):
        super().__init__()
        self.plan_repository = plan_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self) -> List[SubscriptionPlan]:
        """Obtiene todos los planes activos"""
        return await self.plan_repository.get_all_active()
