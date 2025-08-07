from apps.payments.domain.entities import Payment, PaymentStatus
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ..dtos import PaymentResponseDTO


class PaymentEntityDTOMapper(AbstractEntityDtoMapper[Payment, PaymentResponseDTO]):
    """Mapper para convertir entre entidades del dominio y DTOs de Payment."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: Payment) -> PaymentResponseDTO:
        """
        Convierte una entidad del dominio Payment a DTO de respuesta PaymentResponseDTO.
        """
        self.logger.debug(f"Converting entity to DTO for payment {entity.id}")

        return PaymentResponseDTO(
            id=entity.id,
            user_id=entity.user_id,
            stripe_payment_intent_id=entity.stripe_payment_intent_id,
            amount=entity.amount,
            currency=entity.currency,
            status=(
                entity.status.value
                if hasattr(entity.status, "value")
                else str(entity.status)
            ),
            payment_method_id=entity.payment_method_id,
            invoice_id=entity.invoice_id,
            created_at=entity.created_at,
        )

    def dto_to_entity(self, dto: PaymentResponseDTO) -> Payment:
        """
        Convierte un DTO PaymentResponseDTO a entidad del dominio Payment.
        """

        return Payment(
            id=dto.id,
            user_id=dto.user_id,
            stripe_payment_intent_id=dto.stripe_payment_intent_id,
            amount=dto.amount,
            currency=dto.currency,
            status=PaymentStatus(dto.status),
            payment_method_id=dto.payment_method_id,
            invoice_id=dto.invoice_id,
            created_at=dto.created_at,
        )
