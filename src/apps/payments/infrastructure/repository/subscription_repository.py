from typing import Optional

from apps.payments.api.mappers import SubscriptionEntityModelMapper
from common.core.repositories import BaseDjangoRepository

from ...domain.entities import Subscription as SubscriptionEntity
from ...domain.repository import ISubscriptionRepository
from ..models import SubscriptionModel


class SubscriptionRepository(
    BaseDjangoRepository[SubscriptionEntity, SubscriptionModel], ISubscriptionRepository
):
    """Implementación del repositorio de suscripciones usando BaseDjangoRepository"""

    def __init__(self):
        super().__init__(SubscriptionModel, SubscriptionEntityModelMapper())

    async def get_by_user_id(self, user_id: str) -> Optional[SubscriptionEntity]:
        try:
            subscription = await SubscriptionModel.objects.select_related(
                "user", "plan"
            ).aget(user_id=user_id, status__in=["active", "trialing"])
            return self.mapper.model_to_entity(subscription)
        except SubscriptionModel.DoesNotExist:
            return None

    async def get_by_stripe_subscription_id(
        self, stripe_subscription_id: str
    ) -> Optional[SubscriptionEntity]:
        try:
            subscription = await SubscriptionModel.objects.select_related(
                "user", "plan"
            ).aget(stripe_subscription_id=stripe_subscription_id)
            return self.mapper.model_to_entity(subscription)
        except SubscriptionModel.DoesNotExist:
            return None

    async def cancel(self, subscription_id: str) -> bool:
        from django.utils import timezone

        try:
            model = await SubscriptionModel.objects.aget(id=subscription_id)
            model.canceled_at = timezone.now()
            model.status = "canceled"
            await model.asave()
            return True
        except SubscriptionModel.DoesNotExist:
            return False
