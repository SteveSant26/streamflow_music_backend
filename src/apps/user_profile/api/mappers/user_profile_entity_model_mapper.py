from typing import Any, Dict

from apps.user_profile.domain.entities import UserProfileEntity
from apps.user_profile.infrastructure.models import UserProfileModel
from common.interfaces.imapper import AbstractEntityModelMapper


class UserProfileEntityModelMapper(
    AbstractEntityModelMapper[UserProfileEntity, UserProfileModel]
):
    """Mapper para convertir entre entidades del dominio y modelos de UserProfile."""

    def __init__(self):
        super().__init__()

    def model_to_entity(self, model: UserProfileModel) -> UserProfileEntity:
        """
        Convierte un modelo Django UserProfileModel a entidad del dominio UserProfileEntity.
        """
        self.logger.debug(f"Converting model to entity for user {model.id}")
        return UserProfileEntity(
            id=str(model.id),
            email=model.email,
            profile_picture=model.profile_picture,
        )

    def entity_to_model(self, entity: UserProfileEntity) -> UserProfileModel:
        """
        Convierte una entidad UserProfileEntity a una instancia del modelo Django UserProfileModel.
        """
        self.logger.debug(f"Converting entity to model instance for user {entity.id}")
        return UserProfileModel(
            id=entity.id,
            email=entity.email,
            profile_picture=entity.profile_picture,
        )

    def entity_to_model_data(self, entity: UserProfileEntity) -> Dict[str, Any]:
        """
        Convierte una entidad UserProfileEntity a datos del modelo Django (diccionario).
        """
        self.logger.debug(f"Converting entity to model data for user {entity.id}")
        return {
            "email": entity.email,
            "profile_picture": entity.profile_picture,
        }
