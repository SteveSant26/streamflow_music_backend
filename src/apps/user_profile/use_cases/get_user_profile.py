from apps.user_profile.domain.exceptions import UserNotFoundException

from ..domain.entities import UserEntity
from ..infrastructure.repository import UserRepository


class GetUserProfile:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: str) -> UserEntity:
        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        return user
