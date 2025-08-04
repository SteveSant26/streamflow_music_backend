from typing import Optional

from apps.user_profile.api.mappers import UserProfileEntityModelMapper
from apps.user_profile.domain.repository import IUserRepository
from common.core import BaseDjangoRepository

from ...domain.entities import UserProfileEntity
from ...infrastructure.models import UserProfileModel


class UserRepository(
    BaseDjangoRepository[UserProfileEntity, UserProfileModel],
    IUserRepository,
):
    def __init__(self):
        super().__init__(UserProfileModel, UserProfileEntityModelMapper())

    async def get_by_email(self, email: str) -> Optional[UserProfileEntity]:
        """Obtiene un usuario por email"""
        try:
            user = await self.model_class.objects.aget(email=email)
            return self.mapper.model_to_entity(user)
        except self.model_class.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"Error getting user by email {email}: {str(e)}")
            raise
