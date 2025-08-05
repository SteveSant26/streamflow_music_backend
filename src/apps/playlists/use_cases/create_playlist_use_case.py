from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import CreatePlaylistRequestDTO
from ..domain.entities import PlaylistEntity
from ..domain.exceptions import PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class CreatePlaylistUseCase(BaseUseCase[CreatePlaylistRequestDTO, PlaylistEntity]):
    """Caso de uso para crear una nueva playlist"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self, request_dto: CreatePlaylistRequestDTO) -> PlaylistEntity:
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
            # Validar datos requeridos
            if not request_dto.name or not request_dto.name.strip():
                raise PlaylistValidationException(
                    "El nombre de la playlist es requerido"
                )

            if not request_dto.user_id:
                raise PlaylistValidationException("El ID del usuario es requerido")

            # Crear entidad playlist
            import uuid

            from django.utils import timezone

            playlist_entity = PlaylistEntity(
                id=str(uuid.uuid4()),
                name=request_dto.name.strip(),
                description=request_dto.description or "",
                user_id=request_dto.user_id,
                is_public=request_dto.is_public,
                is_default=False,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            self.logger.info(
                f"Creating playlist '{request_dto.name}' for user {request_dto.user_id}"
            )
            return await self.repository.create(playlist_entity)

        except Exception as e:
            self.logger.error(f"Error creating playlist: {str(e)}")
            raise
