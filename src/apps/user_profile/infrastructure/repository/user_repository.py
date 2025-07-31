from typing import Any, Optional

from apps.user_profile.domain.repository import IUserRepository
from src.common.core import BaseDjangoRepository

from ...domain.entities import UserProfileEntity
from ...infrastructure.models import UserProfileModel


class UserRepository(
    BaseDjangoRepository[UserProfileEntity, UserProfileModel], IUserRepository
):
    def __init__(self):
        super().__init__(UserProfileModel)

    # Métodos específicos del repositorio de usuarios (implementación de IUserRepository)

    def get_by_email(self, email: str) -> Optional[UserProfileEntity]:
        """Obtiene un usuario por email"""
        try:
            user = self.model_class.objects.get(email=email)
            return self._model_to_entity(user)
        except self.model_class.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {str(e)}")
            raise

    # Implementación de métodos abstractos del repositorio base

    def _model_to_entity(self, model: UserProfileModel) -> UserProfileEntity:
        """Convierte un modelo UserProfileModel a entidad UserProfileEntity"""
        return UserProfileEntity(
            id=str(model.id),
            email=model.email,
            profile_picture=model.profile_picture,
        )

    def _entity_to_model_data(self, entity: UserProfileEntity) -> dict[str, Any]:
        """Convierte una entidad UserProfileEntity a datos del modelo"""
        return {
            "email": entity.email,
            "profile_picture": entity.profile_picture,
        }

    def _entity_to_model(self, entity: UserProfileEntity) -> UserProfileModel:
        """Convierte una entidad UserProfileEntity a un modelo Django UserProfileModel"""
        try:
            user_data = {
                "email": entity.email,
                "profile_picture": entity.profile_picture,
            }

            # Si la entidad tiene un id (usuario existente), incluirlo
            if hasattr(entity, "id") and entity.id is not None:
                user_data["id"] = entity.id

            self.logger.debug(f"Convirtiendo entidad usuario a modelo: {user_data}")
            user = UserProfileModel(**user_data)
            return user

        except Exception as e:
            self.logger.error(f"Error al convertir entidad usuario a modelo: {str(e)}")
            raise
