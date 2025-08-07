"""
Use case for getting payment methods
"""

from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import PaymentMethodEntity
from ..domain.repository import IPaymentMethodRepository


class GetPaymentMethodsUseCase(BaseUseCase[str, List[PaymentMethodEntity]]):
    """Caso de uso para obtener métodos de pago de un usuario"""

    def __init__(self, payment_method_repository: IPaymentMethodRepository):
        super().__init__()
        self.payment_method_repository = payment_method_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, user_id: str) -> List[PaymentMethodEntity]:
        """Obtiene los métodos de pago del usuario"""
        return await self.payment_method_repository.get_by_user_id(user_id)
