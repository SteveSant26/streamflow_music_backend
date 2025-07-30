from apps.user_profile.domain.exceptions import (
    UserNotFoundException,
    UserProfilePictureUploadException,
)
from common.interfaces import IStorageService
from common.interfaces.ibase_use_case import BaseUseCase

from ..domain.entities import UserProfileEntity
from ..domain.repository import IUserRepository


class UploadProfilePicture(BaseUseCase):
    def __init__(
        self, user_repository: IUserRepository, storage_service: IStorageService
    ):
        super().__init__()
        self.user_repository = user_repository
        self.storage_service = storage_service

    def execute(self, user_id: str, profile_picture_file) -> UserProfileEntity:
        """
        Ejecuta el caso de uso de subir foto de perfil.

        Args:
            user_id: ID del usuario
            profile_picture_file: Archivo de imagen

        Returns:
            UserEntity: Entidad actualizada del usuario

        Raises:
            UserNotFoundException: Si el usuario no existe
            UserProfilePictureUploadException: Si falla la subida
        """
        self.logger.info(f"Uploading profile picture for user {user_id}")

        if not user_id or not profile_picture_file:
            self.logger.warning(f"Invalid data for user {user_id}")
            raise UserProfilePictureUploadException(
                "Error al subir la imagen del perfil."
            )

        user = self.user_repository.get_by_id(user_id)
        if not user:
            self.logger.error(f"User with ID {user_id} not found.")
            raise UserNotFoundException(user_id)

        # Eliminar imagen anterior si existe
        if user.profile_picture:
            self.logger.info(f"Deleting old profile picture for user {user_id}")
            self.storage_service.delete_item(user.profile_picture)

        # Subir nueva imagen
        file_path = f"user_{user_id}.jpg"
        upload_success = self.storage_service.upload_item(
            file_path, profile_picture_file
        )

        if not upload_success:
            self.logger.error(f"Failed to upload profile picture for user {user_id}.")
            raise UserProfilePictureUploadException(
                "Error al subir la imagen del perfil."
            )

        # Actualizar entidad (solo guardamos la ruta, no la URL completa)
        user.profile_picture = file_path
        self.logger.info(f"Profile picture uploaded successfully for user {user_id}")

        return self.user_repository.update(user_id, user)
