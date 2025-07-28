from common.utils.storage_utils import StorageUtils

from ..domain.entities import UserEntity
from ..infrastructure.repository import UserRepository


class UploadProfilePicture:
    def __init__(self, user_repository: UserRepository, image_utils: StorageUtils):
        self.user_repository = user_repository
        self.storage_utils = image_utils

    def execute(self, data: dict) -> UserEntity | None:
        user_id = data.get("id")
        profile_picture = data.get("profile_picture")
        email = data.get("email") or ""

        if not user_id or not profile_picture:
            return None

        file_path = f"profile-pictures/user_{user_id}.jpg"
        uploaded_image_url = self.storage_utils.upload_item(file_path, profile_picture)

        if not uploaded_image_url:
            return None

        # Puedes obtener datos actuales con el repo si quieres, o pasar email en data
        user_entity = UserEntity(
            id=user_id,
            email=email,
            profile_picture=uploaded_image_url,
        )

        print(f"User {user_id} uploaded profile picture: {uploaded_image_url}")

        return self.user_repository.update(user_id, user_entity)
