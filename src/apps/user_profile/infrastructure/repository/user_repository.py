from ...domain.entities import UserEntity
from ...infrastructure.models import UserProfile


class UserRepository:
    def __init__(self):
        self.model = UserProfile

    def get_user_by_id(self, user_id: str) -> UserEntity | None:
        try:
            user = self.model.objects.get(pk=user_id)
            return self._to_entity(user)
        except self.model.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> UserEntity | None:
        try:
            user = self.model.objects.get(email=email)
            return self._to_entity(user)
        except self.model.DoesNotExist:
            return None

    def save(self, user_entity: UserEntity) -> UserEntity:
        print()
        print()
        print()
        print(user_entity.id)

        user, _ = self.model.objects.update_or_create(
            id=user_entity.id,
            email=user_entity.email,
        )

        return self._to_entity(user)

    def _to_entity(self, user: UserProfile) -> UserEntity:
        return UserEntity(
            id=str(user.id),
            email=user.email,
        )
