from uuid import UUID

from apps.playlists.infrastructure.repository import PlaylistRepository
from common.interfaces.ibase_use_case import BaseUseCase


class RemoveSongFromPlaylistUseCase(BaseUseCase[dict, bool]):
    """Caso de uso para remover una canción de una playlist"""
    
    def __init__(self, playlist_repository: PlaylistRepository):
        super().__init__()
        self.playlist_repository = playlist_repository
    
    async def execute(self, request: dict) -> bool:
        """
        Remueve una canción de una playlist
        
        Args:
            request: dict con 'playlist_id' y 'song_id'
        """
        playlist_id = request["playlist_id"]
        song_id = request["song_id"]
        
        self.logger.info(f"Removing song {song_id} from playlist {playlist_id}")
        
        # Verificar que la playlist existe
        playlist = await self.playlist_repository.get_by_id(playlist_id)
        if not playlist:
            raise ValueError(f"Playlist {playlist_id} no encontrada")
        
        # Remover la canción
        success = await self.playlist_repository.remove_song_from_playlist(
            playlist_id, song_id
        )
        
        if success:
            self.logger.info(f"Successfully removed song {song_id} from playlist {playlist_id}")
        else:
            self.logger.warning(f"Song {song_id} was not found in playlist {playlist_id}")
        
        return success
