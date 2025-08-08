import uuid

from django.utils import timezone

from common.interfaces.ibase_use_case import BaseUseCase
from common.interfaces.istorage_service import IStorageService
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import CreatePlaylistRequestDTO
from ..domain.entities import PlaylistEntity
from ..domain.exceptions import (
    PlaylistImageUploadException,
    PlaylistValidationException,
)
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class CreatePlaylistUseCase(BaseUseCase[CreatePlaylistRequestDTO, PlaylistEntity]):
    """Caso de uso para crear una nueva playlist"""

    def __init__(
        self, playlist_repository: IPlaylistRepository, storage_service: IStorageService
    ):
        super().__init__()
        self.repository = playlist_repository
        self.storage_service = storage_service

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(
        self, request_dto: CreatePlaylistRequestDTO, user_id: str
    ) -> PlaylistEntity:
        """
        Crea una nueva playlist

        Args:
            request_dto: DTO con datos de la playlist

        Returns:
            Entidad de playlist creada

        Raises:
            PlaylistValidationException: Si los datos son inválidos
        """
        try:
            if not request_dto.name or not request_dto.name.strip():
                raise PlaylistValidationException(
                    "El nombre de la playlist es requerido"
                )

            if not user_id:
                raise PlaylistValidationException("El ID del usuario es requerido")

            # Generar ID para la playlist antes de crearla
            playlist_id = str(uuid.uuid4())

            # Subir imagen si existe
            playlist_img_path = ""
            if request_dto.playlist_img_file:
                file_path = f"playlist_{playlist_id}.jpg"
                upload_success = self.storage_service.upload_item(
                    file_path, request_dto.playlist_img_file
                )

                if not upload_success:
                    raise PlaylistImageUploadException(
                        "Error al subir la imagen de la playlist"
                    )

                playlist_img_path = file_path

            is_public_value = request_dto.is_public
            if isinstance(is_public_value, str):
                is_public_value = is_public_value.lower() == "true"

            # Crear entidad de playlist
            playlist_entity = PlaylistEntity(
                id=playlist_id,
                name=request_dto.name.strip(),
                description=request_dto.description or "",
                user_id=user_id,
                is_public=is_public_value,
                playlist_img=playlist_img_path,
                is_default=False,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            self.logger.info(
                f"Creating playlist '{request_dto.name}' for user {user_id}"
            )
            playlist = await self.repository.create(playlist_entity)
            self.logger.info(
                f"Created playlist '{playlist.name}' with ID {playlist.id}"
            )
            return playlist

        except Exception as e:
            self.logger.error(f"Error creating playlist: {str(e)}")
            raise
