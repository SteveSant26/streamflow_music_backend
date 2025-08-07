from common.interfaces.imapper.abstract_mapper import AbstractMapper

from .payment_method_entity_dto_mapper import PaymentMethodEntityDTOMapper
from .payment_method_entity_model_mapper import PaymentMethodEntityModelMapper


class PaymentMethodMapper(
    PaymentMethodEntityModelMapper, PaymentMethodEntityDTOMapper, AbstractMapper
):
    """Mapper principal para convertir entre entidades del dominio y modelos/DTOs de PaymentMethod."""

    def __init__(self):
        super().__init__()
