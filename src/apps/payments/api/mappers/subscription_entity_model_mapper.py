from common.interfaces.imapper import AbstractEntityModelMapper

from ...domain.entities import SubscriptionEntity
from ...domain.enums.subscription_status import SubscriptionStatus
from ...infrastructure.models import SubscriptionModel


class SubscriptionEntityModelMapper(
    AbstractEntityModelMapper[SubscriptionEntity, SubscriptionModel]
):
    """Mapper para convertir entre entidades del dominio y modelos de Subscription."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: SubscriptionModel) -> SubscriptionEntity:
        """
        Convierte un modelo Django SubscriptionModel a entidad del dominio Subscription.
        """
        self.logger.info(f"Converting SubscriptionModel {model.id} to entity")
        return SubscriptionEntity(
            id=str(model.id),
            user_id=str(model.user.pk),
            stripe_subscription_id=model.stripe_subscription_id,
            stripe_customer_id=model.stripe_customer_id,
            plan_id=str(model.plan.id),
            status=SubscriptionStatus(model.status),
            current_period_start=model.current_period_start,
            current_period_end=model.current_period_end,
            trial_start=model.trial_start,
            trial_end=model.trial_end,
            canceled_at=model.canceled_at,
            ended_at=model.ended_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def entity_to_model(self, entity: SubscriptionEntity) -> SubscriptionModel:
        """
        Convierte una entidad Subscription a una instancia del modelo Django SubscriptionModel.
        """
        self.logger.info(
            f"Converting Subscription entity {entity.id} to model instance"
        )
        return SubscriptionModel(
            id=entity.id,
            stripe_subscription_id=entity.stripe_subscription_id,
            stripe_customer_id=entity.stripe_customer_id,
            status=(
                entity.status.value
                if hasattr(entity.status, "value")
                else entity.status
            ),
            current_period_start=entity.current_period_start,
            current_period_end=entity.current_period_end,
            trial_start=entity.trial_start,
            trial_end=entity.trial_end,
            canceled_at=entity.canceled_at,
            ended_at=entity.ended_at,
        )

    def entity_to_model_data(self, entity: SubscriptionEntity) -> dict:
        """
        Convierte una entidad Subscription a datos para crear/actualizar un modelo Django.
        """
        self.logger.info(f"Converting Subscription entity {entity.id} to model data")
        return {
            "user_id": entity.user_id,
            "stripe_subscription_id": entity.stripe_subscription_id,
            "stripe_customer_id": entity.stripe_customer_id,
            "plan_id": entity.plan_id,
            "status": (
                entity.status.value
                if hasattr(entity.status, "value")
                else entity.status
            ),
            "current_period_start": entity.current_period_start,
            "current_period_end": entity.current_period_end,
            "trial_start": entity.trial_start,
            "trial_end": entity.trial_end,
            "canceled_at": entity.canceled_at,
            "ended_at": entity.ended_at,
        }
