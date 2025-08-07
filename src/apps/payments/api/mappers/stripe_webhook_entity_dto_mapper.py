from apps.payments.domain.entities import StripeWebhookEventEntity
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ..dtos import StripeWebhookEventResponseDTO


class StripeWebhookEventEntityDTOMapper(
    AbstractEntityDtoMapper[StripeWebhookEventEntity, StripeWebhookEventResponseDTO]
):
    """Mapper para convertir entre entidades del dominio y DTOs de StripeWebhookEvent."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(
        self, entity: StripeWebhookEventEntity
    ) -> StripeWebhookEventResponseDTO:
        """
        Convierte una entidad del dominio StripeWebhookEventEntity a DTO de respuesta StripeWebhookEventResponseDTO.
        """
        self.logger.debug(
            f"Converting entity to DTO for stripe webhook event {entity.id}"
        )

        return StripeWebhookEventResponseDTO(
            id=entity.id,
            stripe_event_id=entity.stripe_event_id,
            event_type=entity.event_type,
            processed=entity.processed,
            data=entity.data,
            created_at=entity.created_at,
            processed_at=entity.processed_at,
        )

    def dto_to_entity(
        self, dto: StripeWebhookEventResponseDTO
    ) -> StripeWebhookEventEntity:
        """
        Convierte un DTO StripeWebhookEventResponseDTO a entidad del dominio StripeWebhookEventEntity.
        """
        self.logger.debug(f"Converting DTO to entity for stripe webhook event {dto.id}")

        return StripeWebhookEventEntity(
            id=dto.id,
            stripe_event_id=dto.stripe_event_id,
            event_type=dto.event_type,
            processed=dto.processed,
            data=dto.data,
            created_at=dto.created_at,
            processed_at=dto.processed_at,
        )
