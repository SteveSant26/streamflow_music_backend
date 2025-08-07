"""
Use case for getting invoice history
"""

from typing import List

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import InvoiceEntity
from ..domain.repository import IInvoiceRepository


class GetInvoiceHistoryUseCase(BaseUseCase[tuple, List[InvoiceEntity]]):
    """Caso de uso para obtener historial de facturas"""

    def __init__(self, invoice_repository: IInvoiceRepository):
        super().__init__()
        self.invoice_repository = invoice_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, user_id: str, limit: int = 10) -> List[InvoiceEntity]:
        """Obtiene el historial de facturas del usuario"""
        return await self.invoice_repository.get_by_user_id(user_id, limit)
