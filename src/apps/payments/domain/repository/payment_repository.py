from abc import abstractmethod
from typing import Any, List, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import Payment


class IPaymentRepository(IBaseRepository[Payment, Any]):
    """Interface para el repositorio de pagos"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str, limit: int = 10) -> List[Payment]:
        """Obtiene los pagos de un usuario"""

    @abstractmethod
    async def get_by_stripe_payment_intent_id(
        self, stripe_payment_intent_id: str
    ) -> Optional[Payment]:
        """Obtiene un pago por su Payment Intent ID de Stripe"""
