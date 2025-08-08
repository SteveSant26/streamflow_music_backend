from typing import List, Optional

from asgiref.sync import sync_to_async

from apps.payments.api.mappers import SubscriptionPlanEntityModelMapper
from common.core.repositories import BaseDjangoRepository

from ...domain.entities import SubscriptionPlanEntity as SubscriptionPlanEntity
from ...domain.repository import ISubscriptionPlanRepository
from ..models import SubscriptionPlanModel


class SubscriptionPlanRepository(
    BaseDjangoRepository[SubscriptionPlanEntity, SubscriptionPlanModel],
    ISubscriptionPlanRepository,
):
    """Implementación del repositorio de planes de suscripción usando BaseDjangoRepository"""

    def __init__(self):
        super().__init__(SubscriptionPlanModel, SubscriptionPlanEntityModelMapper())

    async def get_all_active(self) -> List[SubscriptionPlanEntity]:
        plans = await sync_to_async(SubscriptionPlanModel.objects.filter)(
            is_active=True
        )
        return await sync_to_async(self.mapper.models_to_entities)(plans)

    async def get_by_stripe_price_id(
        self, stripe_price_id: str
    ) -> Optional[SubscriptionPlanEntity]:
        try:
            plan = await SubscriptionPlanModel.objects.aget(
                stripe_price_id=stripe_price_id
            )
            return self.mapper.model_to_entity(plan)
        except SubscriptionPlanModel.DoesNotExist:
            return None
