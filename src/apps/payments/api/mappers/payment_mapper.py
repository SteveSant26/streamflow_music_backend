from common.interfaces.imapper.abstract_mapper import AbstractMapper

from .payment_entity_dto_mapper import PaymentEntityDTOMapper
from .payment_entity_model_mapper import PaymentEntityModelMapper


class PaymentMapper(PaymentEntityModelMapper, PaymentEntityDTOMapper, AbstractMapper):
    """Mapper principal para convertir entre entidades del dominio y modelos/DTOs de Payment."""

    def __init__(self):
        super().__init__()
