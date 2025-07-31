from abc import abstractmethod
from typing import Optional

from apps.user_profile.domain.entities import UserProfileEntity
from apps.user_profile.infrastructure.models.user_profile import UserProfileModel
from common.interfaces.ibase_repository import IBaseRepository


class IUserRepository(IBaseRepository[UserProfileEntity, UserProfileModel]):
    """
    Interface for user repository.
    """

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserProfileEntity]:
        """Obtiene un usuario por email"""
