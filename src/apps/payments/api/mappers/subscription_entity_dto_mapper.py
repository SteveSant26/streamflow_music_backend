from apps.payments.domain.entities import SubscriptionEntity
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ..dtos import SubscriptionResponseDTO


class SubscriptionEntityDTOMapper(
    AbstractEntityDtoMapper[SubscriptionEntity, SubscriptionResponseDTO]
):
    """Mapper para convertir entre entidades del dominio y DTOs de Subscription."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: SubscriptionEntity) -> SubscriptionResponseDTO:
        """
        Convierte una entidad del dominio Subscription a DTO de respuesta SubscriptionResponseDTO.
        """
        self.logger.debug(f"Converting entity to DTO for subscription {entity.id}")

        return SubscriptionResponseDTO(
            id=entity.id,
            user_id=entity.user_id,
            plan_id=entity.plan_id,
            stripe_subscription_id=entity.stripe_subscription_id,
            stripe_customer_id=entity.stripe_customer_id,
            status=(
                entity.status.value
                if hasattr(entity.status, "value")
                else str(entity.status)
            ),
            current_period_start=entity.current_period_start,
            current_period_end=entity.current_period_end,
            trial_start=entity.trial_start,
            trial_end=entity.trial_end,
            canceled_at=entity.canceled_at,
            ended_at=entity.ended_at,
        )
