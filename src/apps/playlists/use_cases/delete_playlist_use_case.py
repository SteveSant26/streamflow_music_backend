from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.exceptions import PlaylistValidationException
from ..domain.repository.iplaylist_repository import IPlaylistRepository


class DeletePlaylistUseCase(BaseUseCase[str, bool]):
    """Caso de uso para eliminar una playlist"""

    def __init__(self, playlist_repository: IPlaylistRepository):
        super().__init__()
        self.repository = playlist_repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, playlist_id: str) -> bool:
        """
        Elimina una playlist

        Args:
            playlist_id: ID de la playlist a eliminar

        Returns:
            True si se eliminó correctamente, False en caso contrario

        Raises:
            PlaylistValidationException: Si los datos son inválidos o la playlist no se puede eliminar
        """
        try:
            if not playlist_id:
                raise PlaylistValidationException("playlist_id es requerido")

            # Verificar que la playlist existe
            playlist = await self.repository.get_by_id(playlist_id)
            if not playlist:
                raise PlaylistValidationException("Playlist no encontrada")

            # No permitir eliminar playlists por defecto (favoritos)
            if playlist.is_default:
                raise PlaylistValidationException(
                    "No se puede eliminar la playlist de favoritos"
                )

            # Eliminar la playlist
            return await self.repository.delete(playlist_id)

        except PlaylistValidationException:
            raise
        except Exception as e:
            self.logger.error(f"Error eliminando playlist: {str(e)}")
            raise PlaylistValidationException(f"Error interno: {str(e)}")
