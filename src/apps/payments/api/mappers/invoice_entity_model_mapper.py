from common.interfaces.imapper import AbstractEntityModelMapper

from ...domain.entities import InvoiceEntity
from ...domain.enums.invoice_status import InvoiceStatus
from ...infrastructure.models import InvoiceModel


class InvoiceEntityModelMapper(AbstractEntityModelMapper[InvoiceEntity, InvoiceModel]):
    """Mapper para convertir entre entidades del dominio y modelos de Invoice."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: InvoiceModel) -> InvoiceEntity:
        """
        Convierte un modelo Django InvoiceModel a entidad del dominio Invoice.
        """
        self.logger.info(f"Converting InvoiceModel {model.id} to entity")
        return InvoiceEntity(
            id=str(model.id),
            user_id=str(model.user.pk),
            subscription_id=str(model.subscription.id) if model.subscription else "",
            stripe_invoice_id=model.stripe_invoice_id,
            amount=model.amount,
            currency=model.currency,
            status=InvoiceStatus(model.status),
            due_date=model.due_date,
            paid_at=model.paid_at,
            created_at=model.created_at,
        )

    def entity_to_model(self, entity: InvoiceEntity) -> InvoiceModel:
        """
        Convierte una entidad Invoice a una instancia del modelo Django InvoiceModel.
        """
        self.logger.info(f"Converting Invoice entity {entity.id} to model instance")
        return InvoiceModel(
            id=entity.id,
            stripe_invoice_id=entity.stripe_invoice_id,
            amount=entity.amount,
            currency=entity.currency,
            status=(
                entity.status.value
                if hasattr(entity.status, "value")
                else entity.status
            ),
            due_date=entity.due_date,
            paid_at=entity.paid_at,
            created_at=entity.created_at,
        )

    def entity_to_model_data(self, entity: InvoiceEntity) -> dict:
        """
        Convierte una entidad Invoice a datos para crear/actualizar un modelo Django.
        """
        self.logger.info(f"Converting Invoice entity {entity.id} to model data")
        return {
            "user_id": entity.user_id,
            "subscription_id": entity.subscription_id,
            "stripe_invoice_id": entity.stripe_invoice_id,
            "amount": entity.amount,
            "currency": entity.currency,
            "status": (
                entity.status.value
                if hasattr(entity.status, "value")
                else entity.status
            ),
            "due_date": entity.due_date,
            "paid_at": entity.paid_at,
        }
