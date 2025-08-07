from common.interfaces.imapper import AbstractEntityModelMapper

from ...domain.entities import StripeWebhookEventEntity
from ...infrastructure.models import StripeWebhookEventModel


class StripeWebhookEventEntityModelMapper(
    AbstractEntityModelMapper[StripeWebhookEventEntity, StripeWebhookEventModel]
):
    """Mapper para convertir entre entidades del dominio y modelos de StripeWebhookEvent."""

    def __init__(self):
        super().__init__()

    def model_to_entity(
        self, model: StripeWebhookEventModel
    ) -> StripeWebhookEventEntity:
        """
        Convierte un modelo Django StripeWebhookEventModel a entidad del dominio StripeWebhookEventEntity.
        """
        self.logger.info(f"Converting StripeWebhookEventModel {model.id} to entity")
        return StripeWebhookEventEntity(
            id=str(model.id),
            stripe_event_id=model.stripe_event_id,
            event_type=model.event_type,
            processed=model.processed,
            data=model.data,
            created_at=model.created_at,
            processed_at=model.processed_at,
        )

    def entity_to_model(
        self, entity: StripeWebhookEventEntity
    ) -> StripeWebhookEventModel:
        """
        Convierte una entidad StripeWebhookEventEntity a una instancia del modelo Django StripeWebhookEventModel.
        """
        self.logger.info(
            f"Converting StripeWebhookEventEntity {entity.id} to model instance"
        )
        return StripeWebhookEventModel(
            id=entity.id,
            stripe_event_id=entity.stripe_event_id,
            event_type=entity.event_type,
            processed=entity.processed,
            data=entity.data,
            created_at=entity.created_at,
            processed_at=entity.processed_at,
        )

    def entity_to_model_data(self, entity: StripeWebhookEventEntity) -> dict:
        """
        Convierte una entidad StripeWebhookEventEntity a datos para crear/actualizar un modelo Django.
        """
        self.logger.info(
            f"Converting StripeWebhookEventEntity {entity.id} to model data"
        )
        return {
            "stripe_event_id": entity.stripe_event_id,
            "event_type": entity.event_type,
            "processed": entity.processed,
            "data": entity.data,
            "processed_at": entity.processed_at,
        }
