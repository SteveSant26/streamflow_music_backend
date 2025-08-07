from apps.payments.domain.entities import InvoiceEntity
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ..dtos import InvoiceResponseDTO


class InvoiceEntityDTOMapper(
    AbstractEntityDtoMapper[InvoiceEntity, InvoiceResponseDTO]
):
    """Mapper para convertir entre entidades del dominio y DTOs de Invoice."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: InvoiceEntity) -> InvoiceResponseDTO:
        """
        Convierte una entidad del dominio Invoice a DTO de respuesta InvoiceResponseDTO.
        """
        self.logger.debug(f"Converting entity to DTO for invoice {entity.id}")

        return InvoiceResponseDTO(
            id=entity.id,
            stripe_invoice_id=entity.stripe_invoice_id,
            subscription_id=entity.subscription_id,
            user_id=entity.user_id,
            amount=entity.amount,
            currency=entity.currency,
            status=(
                entity.status.value
                if hasattr(entity.status, "value")
                else str(entity.status)
            ),
            due_date=entity.due_date,
            paid_at=entity.paid_at,
            created_at=entity.created_at,
        )
