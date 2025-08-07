from typing import List, Optional

from asgiref.sync import sync_to_async

from apps.payments.api.mappers import PaymentEntityModelMapper
from common.core.repositories import BaseDjangoRepository

from ...domain.entities import Payment as PaymentEntity
from ...domain.repository import IPaymentRepository
from ..models import PaymentModel


class PaymentRepository(
    BaseDjangoRepository[PaymentEntity, PaymentModel], IPaymentRepository
):
    """Implementación del repositorio de pagos usando BaseDjangoRepository"""

    def __init__(self):
        super().__init__(PaymentModel, PaymentEntityModelMapper())

    async def get_by_user_id(
        self, user_id: str, limit: int = 10
    ) -> List[PaymentEntity]:
        payments = await sync_to_async(
            lambda: list(PaymentModel.objects.filter(user_id=user_id)[:limit])
        )()
        return self.mapper.models_to_entities(payments)

    async def get_by_stripe_payment_intent_id(
        self, stripe_payment_intent_id: str
    ) -> Optional[PaymentEntity]:
        try:
            payment = await PaymentModel.objects.aget(
                stripe_payment_intent_id=stripe_payment_intent_id
            )
            return self.mapper.model_to_entity(payment)
        except PaymentModel.DoesNotExist:
            return None

    async def update(self, entity_id: str, entity: PaymentEntity) -> PaymentEntity:
        model = await PaymentModel.objects.aget(id=entity_id)
        model.status = entity.status.value
        model.metadata = entity.metadata
        await model.asave()
        return self.mapper.model_to_entity(model)
