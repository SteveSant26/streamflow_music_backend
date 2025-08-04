from uuid import UUID

from apps.playlists.domain.entities import PlaylistSongEntity
from apps.playlists.infrastructure.repository import PlaylistRepository
from common.interfaces.ibase_use_case import BaseUseCase


class AddSongToPlaylistUseCase(BaseUseCase[dict, PlaylistSongEntity]):
    """Caso de uso para agregar una canción a una playlist"""
    
    def __init__(self, playlist_repository: PlaylistRepository):
        super().__init__()
        self.playlist_repository = playlist_repository
    
    async def execute(self, request: dict) -> PlaylistSongEntity:
        """
        Agrega una canción a una playlist
        
        Args:
            request: dict con 'playlist_id', 'song_id', y opcionalmente 'position'
        """
        playlist_id = request["playlist_id"]
        song_id = request["song_id"]
        position = request.get("position")
        
        self.logger.info(f"Adding song {song_id} to playlist {playlist_id}")
        
        # Verificar que la playlist existe
        playlist = await self.playlist_repository.get_by_id(playlist_id)
        if not playlist:
            raise ValueError(f"Playlist {playlist_id} no encontrada")
        
        # Agregar la canción
        playlist_song = await self.playlist_repository.add_song_to_playlist(
            playlist_id, song_id, position
        )
        
        self.logger.info(f"Successfully added song {song_id} to playlist {playlist_id}")
        return playlist_song
