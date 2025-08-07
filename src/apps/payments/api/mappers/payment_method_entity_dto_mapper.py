from apps.payments.domain.entities import PaymentMethod
from common.interfaces.imapper.abstract_entity_dto_mapper import AbstractEntityDtoMapper

from ..dtos import PaymentMethodResponseDTO


class PaymentMethodEntityDTOMapper(
    AbstractEntityDtoMapper[PaymentMethod, PaymentMethodResponseDTO]
):
    """Mapper para convertir entre entidades del dominio y DTOs de PaymentMethod."""

    def __init__(self):
        super().__init__()

    def entity_to_dto(self, entity: PaymentMethod) -> PaymentMethodResponseDTO:
        """
        Convierte una entidad del dominio PaymentMethod a DTO de respuesta PaymentMethodResponseDTO.
        """
        self.logger.debug(f"Converting entity to DTO for payment method {entity.id}")

        return PaymentMethodResponseDTO(
            id=entity.id,
            user_id=entity.user_id,
            stripe_payment_method_id=entity.stripe_payment_method_id,
            type=entity.type,
            card_brand=entity.card_brand,
            card_last4=entity.card_last4,
            card_exp_month=entity.card_exp_month,
            card_exp_year=entity.card_exp_year,
            is_default=entity.is_default,
            created_at=entity.created_at,
        )
