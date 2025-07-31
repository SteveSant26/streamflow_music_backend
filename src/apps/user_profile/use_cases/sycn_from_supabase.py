from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution

from ..domain.entities import UserProfileEntity
from ..infrastructure.repository import UserRepository


class SyncUserFromSupabase(BaseUseCase):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, supabase_data: dict) -> UserProfileEntity:
        self.logger.info("Syncing user from Supabase data")
        metadata = supabase_data.get("user_metadata", {})
        supabase_user_id = supabase_data.get("sub", "")
        supabase_email = supabase_data.get("email", "")

        # Obtener el usuario existente para preservar el profile_picture
        existing_user = self.user_repository.get_by_id(supabase_user_id)
        if existing_user:
            self.logger.debug(
                f"Existing user found: {existing_user.id}, {existing_user.email}, {existing_user.profile_picture}"
            )

        # Usar el profile_picture de Supabase si existe, si no, mantener el existente
        profile_picture = metadata.get("profile_picture")

        if profile_picture is None and existing_user is not None:
            self.logger.debug(
                f"No profile picture in metadata, using existing user's profile picture: {existing_user.profile_picture}"
            )
            profile_picture = existing_user.profile_picture

        user_entity = UserProfileEntity(
            id=supabase_user_id,
            email=supabase_email,
            profile_picture=profile_picture,
        )

        return self.user_repository.save(user_entity)
