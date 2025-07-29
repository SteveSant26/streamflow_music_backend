from apps.user_profile.domain.repository import IUserRepository

from ...domain.entities import UserEntity
from ...infrastructure.models import UserProfile


class UserRepository(IUserRepository):
    def __init__(self):
        self.model = UserProfile

    def get_by_id(self, entity_id: str) -> UserEntity | None:
        try:
            user = self.model.objects.get(pk=entity_id)
            return self._model_to_entity(user)
        except self.model.DoesNotExist:
            return None

    def get_all(self) -> list[UserEntity]:
        query = self.model.objects.all()
        return [self._model_to_entity(user) for user in query]

    def get_by_email(self, email: str) -> UserEntity | None:
        try:
            user = self.model.objects.get(email=email)
            return self._model_to_entity(user)
        except self.model.DoesNotExist:
            return None

    def save(self, entity: UserEntity) -> UserEntity:
        user, _ = self.model.objects.update_or_create(
            id=entity.id,
            email=entity.email,
        )
        return self._model_to_entity(user)

    def delete(self, entity_id: str) -> None:
        self.model.objects.filter(pk=entity_id).delete()

    def update(self, entity_id: str, entity: UserEntity) -> UserEntity:
        user = self.model.objects.get(pk=entity_id)
        user.email = entity.email
        user.profile_picture = entity.profile_picture

        user.save()
        return self._model_to_entity(user)

    def _entity_to_model(self, entity: UserEntity) -> UserProfile:
        return UserProfile(
            id=entity.id,
            email=entity.email,
            profile_picture=entity.profile_picture,
        )

    def _model_to_entity(self, model: UserProfile) -> UserEntity:
        return UserEntity(
            id=str(model.id),
            email=model.email,
            profile_picture=model.profile_picture,
        )
