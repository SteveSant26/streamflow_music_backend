from typing import Optional

from django.utils import timezone

from apps.payments.api.mappers import StripeWebhookEventEntityModelMapper
from common.core.repositories import BaseDjangoRepository

from ...domain.entities import StripeWebhookEventEntity
from ...domain.repository import IStripeWebhookRepository
from ..models import StripeWebhookEventModel


class StripeWebhookRepository(
    BaseDjangoRepository[StripeWebhookEventEntity, StripeWebhookEventModel],
    IStripeWebhookRepository,
):
    """Implementación del repositorio de webhooks de Stripe usando BaseDjangoRepository"""

    def __init__(self):
        super().__init__(StripeWebhookEventModel, StripeWebhookEventEntityModelMapper())

    async def get_by_stripe_event_id(
        self, stripe_event_id: str
    ) -> Optional[StripeWebhookEventEntity]:
        try:
            event = await StripeWebhookEventModel.objects.aget(
                stripe_event_id=stripe_event_id
            )
            return self.mapper.model_to_entity(event)
        except StripeWebhookEventModel.DoesNotExist:
            return None

    async def mark_as_processed(self, event_id: str) -> bool:
        try:
            model = await StripeWebhookEventModel.objects.aget(id=event_id)
            model.processed = True
            model.processed_at = timezone.now()
            await model.asave()
            return True
        except StripeWebhookEventModel.DoesNotExist:
            return False
