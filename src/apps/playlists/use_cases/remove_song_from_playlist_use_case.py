from typing import Any, Dict

from apps.playlists.api.dtos.playlist_dtos import RemoveSongFromPlaylistRequestDTO
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.exceptions import PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class RemoveSongFromPlaylistUseCase(BaseUseCase[Dict[str, Any], bool]):
    """Caso de uso para remover una canción de una playlist"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, request_data: RemoveSongFromPlaylistRequestDTO) -> bool:
        """
        Remueve una canción de una playlist

        Args:
            request_data: Diccionario con playlist_id y song_id

        Returns:
            True si se removió correctamente, False en caso contrario

        Raises:
            PlaylistValidationException: Si los datos son inválidos
        """
        try:
            playlist_id = request_data.playlist_id
            song_id = request_data.song_id

            if not playlist_id or not song_id:
                raise PlaylistValidationException(
                    "playlist_id y song_id son requeridos"
                )

            # Verificar que la playlist existe
            playlist = await self.repository.get_by_id(playlist_id)
            if not playlist:
                raise PlaylistValidationException("Playlist no encontrada")

            # Remover la canción
            return await self.repository.remove_song_from_playlist(playlist_id, song_id)

        except PlaylistValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error removiendo canción de playlist: {str(e)}")
            raise PlaylistValidationException(f"Error interno: {str(e)}")
