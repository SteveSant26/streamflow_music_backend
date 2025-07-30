from apps.user_profile.domain.repository import IUserRepository
from src.common.utils import get_logger

from ...domain.entities import UserProfileEntity
from ...infrastructure.models import UserProfile

logger = get_logger(__name__)


class UserRepository(IUserRepository[UserProfile]):
    def __init__(self):
        self.model = UserProfile

    def get_by_id(self, entity_id: str) -> UserProfileEntity | None:
        try:
            user = self.model.objects.get(pk=entity_id)
            return self._model_to_entity(user)
        except self.model.DoesNotExist:
            return None

    def get_all(self) -> list[UserProfileEntity]:
        query = self.model.objects.all()
        return [self._model_to_entity(user) for user in query]

    def get_by_email(self, email: str) -> UserProfileEntity | None:
        try:
            user = self.model.objects.get(email=email)
            return self._model_to_entity(user)
        except self.model.DoesNotExist:
            return None

    def save(self, entity: UserProfileEntity) -> UserProfileEntity:
        user, _ = self.model.objects.update_or_create(
            id=entity.id,
            defaults={
                "email": entity.email,
                "profile_picture": entity.profile_picture,
            },
        )
        return self._model_to_entity(user)

    def delete(self, entity_id: str) -> None:
        self.model.objects.filter(pk=entity_id).delete()

    def update(self, entity_id: str, entity: UserProfileEntity) -> UserProfileEntity:
        logger.info(
            f"Updating user {entity_id} with profile_picture: {entity.profile_picture}"
        )
        user = self.model.objects.get(pk=entity_id)

        old_profile_picture = user.profile_picture
        logger.debug(f"Old profile_picture: {old_profile_picture}")

        user.email = entity.email
        user.profile_picture = entity.profile_picture

        logger.debug(f"New profile_picture: {user.profile_picture}")
        user.save()

        # Verificar que se guardó correctamente
        updated_user = self.model.objects.get(pk=entity_id)
        logger.info(
            f"User {entity_id} updated. Current profile_picture in DB: {updated_user.profile_picture}"
        )

        return self._model_to_entity(updated_user)

    def _entity_to_model(self, entity: UserProfileEntity) -> UserProfile:
        return UserProfile(
            id=entity.id,
            email=entity.email,
            profile_picture=entity.profile_picture,
        )

    def _model_to_entity(self, model: UserProfile) -> UserProfileEntity:
        return UserProfileEntity(
            id=str(model.id),
            email=model.email,
            profile_picture=model.profile_picture,
        )
