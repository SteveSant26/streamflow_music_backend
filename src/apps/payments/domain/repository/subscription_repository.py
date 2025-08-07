from abc import abstractmethod
from typing import Any, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import Subscription


class ISubscriptionRepository(IBaseRepository[Subscription, Any]):
    """Interface para el repositorio de suscripciones"""

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[Subscription]:
        """Obtiene la suscripción activa de un usuario"""

    @abstractmethod
    async def get_by_stripe_subscription_id(
        self, stripe_subscription_id: str
    ) -> Optional[Subscription]:
        """Obtiene una suscripción por su ID de Stripe"""

    @abstractmethod
    async def cancel(self, subscription_id: str) -> bool:
        """Cancela una suscripción"""
