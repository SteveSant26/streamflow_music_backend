from abc import abstractmethod
from typing import Any, List, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import PaymentMethodEntity


class IPaymentMethodRepository(IBaseRepository[PaymentMethodEntity, Any]):
    """Interface para el repositorio de métodos de pago"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[PaymentMethodEntity]:
        """Obtiene todos los métodos de pago de un usuario"""

    @abstractmethod
    async def get_default_by_user_id(
        self, user_id: str
    ) -> Optional[PaymentMethodEntity]:
        """Obtiene el método de pago por defecto de un usuario"""
