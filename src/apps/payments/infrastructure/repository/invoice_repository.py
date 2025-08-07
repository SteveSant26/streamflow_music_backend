from typing import List, Optional

from asgiref.sync import sync_to_async

from common.core.repositories import BaseDjangoRepository

from ...api.mappers import InvoiceEntityModelMapper
from ...domain.entities import InvoiceEntity
from ...domain.repository import IInvoiceRepository
from ..models import InvoiceModel


class InvoiceRepository(
    BaseDjangoRepository[InvoiceEntity, InvoiceModel], IInvoiceRepository
):
    """Implementación del repositorio de facturas usando BaseDjangoRepository"""

    def __init__(self):
        super().__init__(InvoiceModel, InvoiceEntityModelMapper())

    async def get_by_user_id(self, user_id: str) -> List[InvoiceEntity]:
        def get_invoices():
            return list(
                InvoiceModel.objects.filter(user_id=user_id).order_by("-created_at")
            )

        invoices = await sync_to_async(get_invoices)()
        return self.mapper.models_to_entities(invoices)

    async def get_by_stripe_invoice_id(
        self, stripe_invoice_id: str
    ) -> Optional[InvoiceEntity]:
        try:
            invoice = await InvoiceModel.objects.aget(
                stripe_invoice_id=stripe_invoice_id
            )
            return self.mapper.model_to_entity(invoice)
        except InvoiceModel.DoesNotExist:
            return None
