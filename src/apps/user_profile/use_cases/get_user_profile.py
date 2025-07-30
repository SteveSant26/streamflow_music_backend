from apps.user_profile.domain.exceptions import UserNotFoundException

from ..domain.entities import UserProfileEntity
from ..infrastructure.repository import UserRepository


class GetUserProfileUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def execute(self, user_id: str) -> UserProfileEntity:
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)
        print()
        print()
        print()
        print("User retrieved:", user)
        print("User retrieved:", user.id, user.email, user.profile_picture)
        return user


# from apps.user_profile.domain.exceptions import UserNotFoundException
# from common.interfaces.ibase_use_case import BaseGetByIdUseCase

# from ..domain.entities import UserProfileEntity
# from ..infrastructure.repository import UserRepository


# class GetUserProfileUseCase(BaseGetByIdUseCase[UserProfileEntity]):
#     def __init__(self, repository: UserRepository):
#         super().__init__(repository)

#     def _get_not_found_exception(self, entity_id: str) -> Exception:
#         return UserNotFoundException(entity_id)
