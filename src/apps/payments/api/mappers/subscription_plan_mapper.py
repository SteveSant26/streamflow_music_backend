from common.interfaces.imapper.abstract_mapper import AbstractMapper

from .subscription_plan_entity_dto_mapper import SubscriptionPlanEntityDTOMapper
from .subscription_plan_entity_model_mapper import SubscriptionPlanEntityModelMapper


class SubscriptionPlanMapper(
    SubscriptionPlanEntityModelMapper, SubscriptionPlanEntityDTOMapper, AbstractMapper
):
    """Mapper principal para convertir entre entidades del dominio y modelos/DTOs de SubscriptionPlan."""

    def __init__(self):
        super().__init__()
