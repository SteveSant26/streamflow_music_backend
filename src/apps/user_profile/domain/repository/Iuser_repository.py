from abc import abstractmethod
from apps.user_profile.domain.entities import UserEntity
from apps.user_profile.infrastructure.models.user_profile import UserProfile
from common.interfaces.IBaseRepository import IBaseRepository


class IUserRepository(IBaseRepository[UserEntity, UserProfile]):
    """
    Interface for user repository.
    """

    @abstractmethod
    def get_by_email(self, email: str) -> UserEntity | None:
        ...
