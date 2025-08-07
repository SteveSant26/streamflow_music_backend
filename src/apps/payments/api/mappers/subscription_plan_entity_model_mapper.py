from common.interfaces.imapper import AbstractEntityModelMapper

from ...domain.entities import SubscriptionPlan
from ...infrastructure.models import SubscriptionPlanModel


class SubscriptionPlanEntityModelMapper(
    AbstractEntityModelMapper[SubscriptionPlan, SubscriptionPlanModel]
):
    """Mapper para convertir entre entidades del dominio y modelos de SubscriptionPlan."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: SubscriptionPlanModel) -> SubscriptionPlan:
        """
        Convierte un modelo Django SubscriptionPlanModel a entidad del dominio SubscriptionPlan.
        """
        self.logger.info(f"Converting SubscriptionPlanModel {model.id} to entity")
        return SubscriptionPlan(
            id=str(model.id),
            name=model.name,
            description=model.description,
            price=model.price,
            currency=model.currency,
            interval=model.interval,
            interval_count=model.interval_count,
            features=model.features,
            stripe_price_id=model.stripe_price_id,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def entity_to_model(self, entity: SubscriptionPlan) -> SubscriptionPlanModel:
        """
        Convierte una entidad SubscriptionPlan a una instancia del modelo Django SubscriptionPlanModel.
        """
        self.logger.info(
            f"Converting SubscriptionPlan entity {entity.id} to model instance"
        )
        return SubscriptionPlanModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            price=entity.price,
            currency=entity.currency,
            interval=entity.interval,
            interval_count=entity.interval_count,
            features=entity.features,
            stripe_price_id=entity.stripe_price_id,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def entity_to_model_data(self, entity: SubscriptionPlan) -> dict:
        """
        Convierte una entidad SubscriptionPlan a datos para crear/actualizar un modelo Django.
        """
        self.logger.info(
            f"Converting SubscriptionPlan entity {entity.id} to model data"
        )
        return {
            "name": entity.name,
            "description": entity.description,
            "price": entity.price,
            "currency": entity.currency,
            "interval": entity.interval,
            "interval_count": entity.interval_count,
            "features": entity.features,
            "stripe_price_id": entity.stripe_price_id,
            "is_active": entity.is_active,
        }
