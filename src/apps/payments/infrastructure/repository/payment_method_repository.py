from typing import List, Optional

from asgiref.sync import sync_to_async

from apps.payments.api.mappers import PaymentMethodEntityModelMapper
from common.core.repositories import BaseDjangoRepository

from ...domain.entities import PaymentMethod as PaymentMethodEntity
from ...domain.repository import IPaymentMethodRepository
from ..models.payment_method import PaymentMethodModel


class PaymentMethodRepository(
    BaseDjangoRepository[PaymentMethodEntity, PaymentMethodModel],
    IPaymentMethodRepository,
):
    """Implementación del repositorio de métodos de pago usando BaseDjangoRepository"""

    def __init__(self):
        super().__init__(PaymentMethodModel, PaymentMethodEntityModelMapper())

    async def get_by_user_id(self, user_id: str) -> List[PaymentMethodEntity]:
        models = await sync_to_async(PaymentMethodModel.objects.filter)(user_id=user_id)
        return self.mapper.models_to_entities(models)

    async def get_default_by_user_id(
        self, user_id: str
    ) -> Optional[PaymentMethodEntity]:
        try:
            model = await PaymentMethodModel.objects.aget(
                user_id=user_id, is_default=True
            )
            return self.mapper.model_to_entity(model)
        except PaymentMethodModel.DoesNotExist:
            return None
