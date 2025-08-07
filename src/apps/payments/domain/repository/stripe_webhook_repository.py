from abc import ABC, abstractmethod
from typing import Optional

from ..entities import StripeWebhookEventEntity


class IStripeWebhookRepository(ABC):
    """Interface para el repositorio de webhooks de Stripe"""

    @abstractmethod
    async def get_by_stripe_event_id(
        self, stripe_event_id: str
    ) -> Optional[StripeWebhookEventEntity]:
        """Obtiene un evento por su ID de Stripe"""

    @abstractmethod
    async def mark_as_processed(self, event_id: str) -> bool:
        """Marca un evento como procesado"""
