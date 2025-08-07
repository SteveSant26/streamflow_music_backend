from common.interfaces.imapper.abstract_mapper import AbstractMapper

from .subscription_entity_dto_mapper import SubscriptionEntityDTOMapper
from .subscription_entity_model_mapper import SubscriptionEntityModelMapper


class SubscriptionMapper(
    SubscriptionEntityModelMapper, SubscriptionEntityDTOMapper, AbstractMapper
):
    """Mapper principal para convertir entre entidades del dominio y modelos/DTOs de Subscription."""

    def __init__(self):
        super().__init__()
