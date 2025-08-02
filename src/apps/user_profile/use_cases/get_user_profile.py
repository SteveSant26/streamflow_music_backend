from typing import Any

from apps.user_profile.domain.exceptions import UserNotFoundException
from common.interfaces.ibase_use_case import BaseGetByIdUseCase

from ..domain.entities import UserProfileEntity
from ..domain.repository import IUserRepository


class GetUserProfileUseCase(BaseGetByIdUseCase[UserProfileEntity, Any]):
    def __init__(self, repository: IUserRepository):
        super().__init__(repository)

    def _get_not_found_exception(self, entity_id: str) -> Exception:
        return UserNotFoundException(entity_id)
