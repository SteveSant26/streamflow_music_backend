from common.interfaces.imapper.abstract_mapper import AbstractMapper

from .stripe_webhook_entity_dto_mapper import StripeWebhookEventEntityDTOMapper
from .stripe_webhook_entity_model_mapper import StripeWebhookEventEntityModelMapper


class StripeWebhookEventMapper(
    StripeWebhookEventEntityModelMapper,
    StripeWebhookEventEntityDTOMapper,
    AbstractMapper,
):
    """Mapper principal para convertir entre entidades del dominio y modelos/DTOs de StripeWebhookEvent."""

    def __init__(self):
        super().__init__()
