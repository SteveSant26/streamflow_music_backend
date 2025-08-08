from abc import abstractmethod
from typing import Any, List, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import InvoiceEntity


class IInvoiceRepository(IBaseRepository[InvoiceEntity, Any]):
    """Interface para el repositorio de facturas"""

    @abstractmethod
    async def get_by_user_id(self, user_profile_id: str) -> List[InvoiceEntity]:
        """Obtiene las facturas de un usuario"""

    @abstractmethod
    async def get_by_stripe_invoice_id(
        self, stripe_invoice_id: str
    ) -> Optional[InvoiceEntity]:
        """Obtiene una factura por su ID de Stripe"""
