from apps.user_profile.domain.exceptions import (
    UserNotFoundException,
    UserProfilePictureUploadException,
)
from common.interfaces import IStorageService
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import UploadProfilePictureRequestDTO
from ..domain.entities import UserProfileEntity
from ..domain.repository import IUserRepository


class UploadProfilePicture(
    BaseUseCase[UploadProfilePictureRequestDTO, UserProfileEntity]
):
    def __init__(
        self, user_repository: IUserRepository, storage_service: IStorageService
    ):
        super().__init__()
        self.user_repository = user_repository
        self.storage_service = storage_service

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=5.0)  # Subida de archivos puede tomar tiempo
    async def execute(
        self, request_dto: UploadProfilePictureRequestDTO
    ) -> UserProfileEntity:
        """
        Ejecuta el caso de uso de subir foto de perfil.

        Args:
            request_dto: DTO con user_id, email y profile_picture_file

        Returns:
            UserEntity: Entidad actualizada del usuario

        Raises:
            UserNotFoundException: Si el usuario no existe
            UserProfilePictureUploadException: Si falla la subida
        """
        self.logger.info(f"Uploading profile picture for user {request_dto.user_id}")

        if not request_dto.user_id or not request_dto.profile_picture_file:
            self.logger.warning(f"Invalid data for user {request_dto.user_id}")
            raise UserProfilePictureUploadException(
                "Error al subir la imagen del perfil."
            )

        user = await self.user_repository.get_by_id(request_dto.user_id)
        if not user:
            self.logger.error(f"User with ID {request_dto.user_id} not found.")
            raise UserNotFoundException(request_dto.user_id)

        # Subir nueva imagen
        file_path = f"user_{request_dto.user_id}.jpg"
        upload_success = self.storage_service.upload_item(
            file_path, request_dto.profile_picture_file
        )

        if not upload_success:
            self.logger.error(
                f"Failed to upload profile picture for user {request_dto.user_id}."
            )
            raise UserProfilePictureUploadException(
                "Error al subir la imagen del perfil."
            )

        # Actualizar entidad (solo guardamos la ruta, no la URL completa)
        user.profile_picture = file_path
        self.logger.info(
            f"Profile picture uploaded successfully for user {request_dto.user_id}"
        )

        return await self.user_repository.update(request_dto.user_id, user)
