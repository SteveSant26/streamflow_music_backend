from abc import abstractmethod

from apps.user_profile.domain.entities import UserProfileEntity
from common.interfaces.ibase_repository import IBaseRepository
from common.types import ModelType


class IUserRepository(IBaseRepository[UserProfileEntity, ModelType]):
    """
    Interface for user repository.
    """

    @abstractmethod
    def get_by_email(self, email: str) -> UserProfileEntity | None:
        ...
