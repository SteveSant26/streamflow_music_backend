from apps.payments.domain.entities import SubscriptionPlan
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ..dtos import SubscriptionPlanResponseDTO


class SubscriptionPlanEntityDTOMapper(
    AbstractEntityDtoMapper[SubscriptionPlan, SubscriptionPlanResponseDTO]
):
    """Mapper para convertir entre entidades del dominio y DTOs de SubscriptionPlan."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: SubscriptionPlan) -> SubscriptionPlanResponseDTO:
        """
        Convierte una entidad del dominio SubscriptionPlan a DTO de respuesta SubscriptionPlanResponseDTO.
        """
        self.logger.debug(f"Converting entity to DTO for subscription plan {entity.id}")

        return SubscriptionPlanResponseDTO(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            price=entity.price,
            currency=entity.currency,
            interval=entity.interval,
            interval_count=entity.interval_count,
            features=entity.features,
            stripe_price_id=entity.stripe_price_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def dto_to_entity(self, dto: SubscriptionPlanResponseDTO) -> SubscriptionPlan:
        """
        Convierte un DTO SubscriptionPlanResponseDTO a entidad del dominio SubscriptionPlan.
        """
        return SubscriptionPlan(
            id=dto.id,
            name=dto.name,
            description=dto.description,
            price=dto.price,
            currency=dto.currency,
            interval=dto.interval,
            interval_count=dto.interval_count,
            features=dto.features,
            stripe_price_id=dto.stripe_price_id,
            is_active=dto.is_active,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
