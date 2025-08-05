from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..api.dtos import AddSongToPlaylistRequestDTO
from ..domain.entities import PlaylistSongEntity
from ..domain.exceptions import (
    PlaylistNotFoundException,
    PlaylistSongAlreadyExistsException,
    PlaylistValidationException,
)
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class AddSongToPlaylistUseCase(
    BaseUseCase[AddSongToPlaylistRequestDTO, PlaylistSongEntity]
):
    """Caso de uso para añadir una canción a una playlist"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(
        self, request_dto: AddSongToPlaylistRequestDTO
    ) -> PlaylistSongEntity:
        """
        Añade una canción a una playlist

        Args:
            request_dto: DTO con datos de la canción a añadir

        Returns:
            Entidad PlaylistSong creada

        Raises:
            PlaylistValidationException: Si los datos son inválidos
            PlaylistNotFoundException: Si la playlist no existe
            PlaylistSongAlreadyExistsException: Si la canción ya está en la playlist
        """
        try:
            if not request_dto.playlist_id:
                raise PlaylistValidationException("El ID de la playlist es requerido")

            if not request_dto.song_id:
                raise PlaylistValidationException("El ID de la canción es requerido")

            # Verificar que la playlist existe
            playlist = await self.repository.get_by_id(request_dto.playlist_id)
            if not playlist:
                raise PlaylistNotFoundException(
                    f"Playlist con ID {request_dto.playlist_id} no encontrada"
                )

            # Verificar que la canción no esté ya en la playlist
            song_exists = await self.repository.is_song_in_playlist(
                request_dto.playlist_id, request_dto.song_id
            )
            if song_exists:
                raise PlaylistSongAlreadyExistsException(
                    f"La canción {request_dto.song_id} ya está en la playlist {request_dto.playlist_id}"
                )

            self.logger.info(
                f"Adding song {request_dto.song_id} to playlist {request_dto.playlist_id}"
            )
            return await self.repository.add_song_to_playlist(
                request_dto.playlist_id, request_dto.song_id, request_dto.position
            )

        except Exception as e:
            self.logger.error(f"Error adding song to playlist: {str(e)}")
            raise
