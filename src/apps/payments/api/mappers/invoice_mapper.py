from common.interfaces.imapper.abstract_mapper import AbstractMapper

from .invoice_entity_dto_mapper import InvoiceEntityDTOMapper
from .invoice_entity_model_mapper import InvoiceEntityModelMapper


class InvoiceMapper(InvoiceEntityModelMapper, InvoiceEntityDTOMapper, AbstractMapper):
    """Mapper principal para convertir entre entidades del dominio y modelos/DTOs de Invoice."""

    def __init__(self):
        super().__init__()
