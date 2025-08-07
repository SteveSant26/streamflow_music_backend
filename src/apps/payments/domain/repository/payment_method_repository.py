from abc import abstractmethod
from typing import Any, List, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import PaymentMethod


class IPaymentMethodRepository(IBaseRepository[PaymentMethod, Any]):
    """Interface para el repositorio de métodos de pago"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[PaymentMethod]:
        """Obtiene todos los métodos de pago de un usuario"""

    @abstractmethod
    async def get_default_by_user_id(self, user_id: str) -> Optional[PaymentMethod]:
        """Obtiene el método de pago por defecto de un usuario"""
