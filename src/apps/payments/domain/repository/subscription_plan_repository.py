from abc import abstractmethod
from typing import Any, List, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import SubscriptionPlanEntity


class ISubscriptionPlanRepository(IBaseRepository[SubscriptionPlanEntity, Any]):
    """Interface para el repositorio de planes de suscripción"""

    @abstractmethod
    async def get_all_active(self) -> List[SubscriptionPlanEntity]:
        """Obtiene todos los planes activos"""

    @abstractmethod
    async def get_by_id(self, entity_id: Any) -> Optional[SubscriptionPlanEntity]:
        """Obtiene un plan por ID"""

    @abstractmethod
    async def get_by_stripe_price_id(
        self, stripe_price_id: str
    ) -> Optional[SubscriptionPlanEntity]:
        """Obtiene un plan por el price ID de Stripe"""
