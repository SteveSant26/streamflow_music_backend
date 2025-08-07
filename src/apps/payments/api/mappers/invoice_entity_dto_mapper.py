from apps.payments.domain.entities import InvoiceEntity
from apps.payments.domain.enums import InvoiceStatus
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

    def dto_to_entity(self, dto: InvoiceResponseDTO) -> InvoiceEntity:
        """
        Convierte un DTO a entidad del dominio Invoice.
        """
        self.logger.debug(f"Converting DTO to entity for invoice {dto.id}")

        # Convertir string de status a enum
        if isinstance(dto.status, str):
            try:
                invoice_status = InvoiceStatus(dto.status)
            except ValueError:
                # Si no se puede convertir, usar un valor por defecto
                invoice_status = InvoiceStatus.DRAFT
        else:
            invoice_status = dto.status

        return InvoiceEntity(
            id=dto.id,
            stripe_invoice_id=dto.stripe_invoice_id,
            subscription_id=dto.subscription_id,
            user_id=dto.user_id,
            amount=dto.amount,
            currency=dto.currency,
            status=invoice_status,
            due_date=dto.due_date,
            paid_at=dto.paid_at,
            created_at=dto.created_at,
        )
