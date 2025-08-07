from abc import abstractmethod
from typing import Any, List, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import Invoice


class IInvoiceRepository(IBaseRepository[Invoice, Any]):
    """Interface para el repositorio de facturas"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Invoice]:
        """Obtiene las facturas de un usuario"""

    @abstractmethod
    async def get_by_stripe_invoice_id(
        self, stripe_invoice_id: str
    ) -> Optional[Invoice]:
        """Obtiene una factura por su ID de Stripe"""
