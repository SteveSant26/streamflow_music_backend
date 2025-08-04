from uuid import UUID

from apps.playlists.infrastructure.repository import PlaylistRepository
from common.interfaces.ibase_use_case import BaseUseCase


class DeletePlaylistUseCase(BaseUseCase[UUID, bool]):
    """Caso de uso para eliminar una playlist"""
    
    def __init__(self, playlist_repository: PlaylistRepository):
        super().__init__()
        self.playlist_repository = playlist_repository
    
    async def execute(self, playlist_id: UUID) -> bool:
        """
        Elimina una playlist (solo si no es default)
        """
        self.logger.info(f"Deleting playlist {playlist_id}")
        
        # Verificar que la playlist existe
        playlist = await self.playlist_repository.get_by_id(playlist_id)
        if not playlist:
            raise ValueError(f"Playlist {playlist_id} no encontrada")
        
        # No permitir eliminar playlists default
        if playlist.is_default:
            raise ValueError("No se puede eliminar una playlist por defecto")
        
        # Eliminar la playlist
        success = await self.playlist_repository.delete(playlist_id)
        
        if success:
            self.logger.info(f"Successfully deleted playlist {playlist_id}")
        else:
            self.logger.warning(f"Failed to delete playlist {playlist_id}")
        
        return success
