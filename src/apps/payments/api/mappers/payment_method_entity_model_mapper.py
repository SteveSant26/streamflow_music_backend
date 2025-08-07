from typing import Any, Dict

from common.interfaces.imapper import AbstractEntityModelMapper

from ...domain.entities import PaymentMethod
from ...infrastructure.models.payment_method import PaymentMethodModel


class PaymentMethodEntityModelMapper(
    AbstractEntityModelMapper[PaymentMethod, PaymentMethodModel]
):
    """Mapper para convertir entre entidades del dominio y modelos de PaymentMethod."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: PaymentMethodModel) -> PaymentMethod:
        """
        Convierte un modelo Django PaymentMethodModel a entidad del dominio PaymentMethod.
        """
        self.logger.debug(f"Converting model to entity for payment method {model.id}")
        return PaymentMethod(
            id=str(model.id),
            user_id=str(model.user.pk),
            stripe_payment_method_id=model.stripe_payment_method_id,
            type=model.type,
            card_brand=model.card_brand,
            card_last4=model.card_last4,
            card_exp_month=model.card_exp_month,
            card_exp_year=model.card_exp_year,
            is_default=model.is_default,
            created_at=model.created_at,
        )

    def entity_to_model_data(self, entity: PaymentMethod) -> Dict[str, Any]:
        """
        Convierte una entidad PaymentMethod a datos para crear/actualizar un modelo Django.
        """
        self.logger.debug(
            f"Converting entity to model data for payment method {entity.id}"
        )
        return {
            "stripe_payment_method_id": entity.stripe_payment_method_id,
            "type": entity.type,
            "card_brand": entity.card_brand,
            "card_last4": entity.card_last4,
            "card_exp_month": entity.card_exp_month,
            "card_exp_year": entity.card_exp_year,
            "is_default": entity.is_default,
        }

    def entity_to_model(self, entity: PaymentMethod) -> PaymentMethodModel:
        """
        Convierte una entidad PaymentMethod a una instancia del modelo Django PaymentMethodModel.
        """
        self.logger.debug(
            f"Converting entity to model instance for payment method {entity.id}"
        )
        model_instance = PaymentMethodModel(
            id=entity.id,
            stripe_payment_method_id=entity.stripe_payment_method_id,
            type=entity.type,
            card_brand=entity.card_brand,
            card_last4=entity.card_last4,
            card_exp_month=entity.card_exp_month,
            card_exp_year=entity.card_exp_year,
            is_default=entity.is_default,
            created_at=entity.created_at,
        )
        return model_instance
