from common.interfaces.imapper import AbstractEntityModelMapper

from ...domain.entities import PaymentEntity
from ...domain.enums.payment_status import PaymentStatus
from ...infrastructure.models import PaymentModel


class PaymentEntityModelMapper(AbstractEntityModelMapper[PaymentEntity, PaymentModel]):
    """Mapper para convertir entre entidades del dominio y modelos de Payment."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: PaymentModel) -> PaymentEntity:
        """
        Convierte un modelo Django PaymentModel a entidad del dominio Payment.
        """
        self.logger.info(f"Converting PaymentModel {model.id} to entity")
        return PaymentEntity(
            id=str(model.id),
            user_id=str(model.user.pk),
            invoice_id=str(model.invoice.id) if model.invoice else None,
            payment_method_id=(
                str(model.payment_method.id) if model.payment_method else None
            ),
            stripe_payment_intent_id=model.stripe_payment_intent_id,
            amount=model.amount,
            currency=model.currency,
            status=PaymentStatus(model.status),
            created_at=model.created_at,
        )

    def entity_to_model(self, entity: PaymentEntity) -> PaymentModel:
        """
        Convierte una entidad Payment a una instancia del modelo Django PaymentModel.
        """
        self.logger.info(f"Converting Payment entity {entity.id} to model instance")
        return PaymentModel(
            id=entity.id,
            stripe_payment_intent_id=entity.stripe_payment_intent_id,
            amount=entity.amount,
            currency=entity.currency,
            status=(
                entity.status.value
                if hasattr(entity.status, "value")
                else entity.status
            ),
            created_at=entity.created_at,
        )

    def entity_to_model_data(self, entity: PaymentEntity) -> dict:
        """
        Convierte una entidad Payment a datos para crear/actualizar un modelo Django.
        """
        self.logger.info(f"Converting Payment entity {entity.id} to model data")
        return {
            "user_id": entity.user_id,
            "invoice_id": entity.invoice_id,
            "payment_method_id": entity.payment_method_id,
            "stripe_payment_intent_id": entity.stripe_payment_intent_id,
            "amount": entity.amount,
            "currency": entity.currency,
            "status": (
                entity.status.value
                if hasattr(entity.status, "value")
                else entity.status
            ),
        }
