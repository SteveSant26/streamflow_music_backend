from typing import List
from uuid import UUID

from apps.playlists.api.dtos.playlist_dtos import PlaylistSongResponseDTO
from apps.playlists.infrastructure.repository import PlaylistRepository
from apps.songs.infrastructure.repository import SongRepository
from common.interfaces.ibase_use_case import BaseUseCase


class GetPlaylistSongsUseCase(BaseUseCase[UUID, List[PlaylistSongResponseDTO]]):
    """Caso de uso para obtener las canciones de una playlist"""
    
    def __init__(self, playlist_repository: PlaylistRepository, song_repository: SongRepository):
        super().__init__()
        self.playlist_repository = playlist_repository
        self.song_repository = song_repository
    
    async def execute(self, playlist_id: UUID) -> List[PlaylistSongResponseDTO]:
        """
        Obtiene todas las canciones de una playlist con información completa
        """
        self.logger.info(f"Getting songs for playlist {playlist_id}")
        
        # Verificar que la playlist existe
        playlist = await self.playlist_repository.get_by_id(playlist_id)
        if not playlist:
            raise ValueError(f"Playlist {playlist_id} no encontrada")
        
        # Obtener las canciones de la playlist
        playlist_songs = await self.playlist_repository.get_playlist_songs(playlist_id)
        
        # Construir la respuesta con información completa de las canciones
        songs_response = []
        for playlist_song in playlist_songs:
            # Obtener información completa de la canción
            song = await self.song_repository.get_by_id(playlist_song.song_id)
            
            if song:
                song_dto = PlaylistSongResponseDTO(
                    id=song.id,
                    title=song.title,
                    artist_name=song.artist.name if song.artist else None,
                    album_name=song.album.title if song.album else None,
                    duration_seconds=song.duration_seconds,
                    thumbnail_url=song.thumbnail_url,
                    position=playlist_song.position,
                    added_at=playlist_song.added_at,
                )
                songs_response.append(song_dto)
        
        # Ordenar por posición
        songs_response.sort(key=lambda x: x.position)
        
        self.logger.info(f"Found {len(songs_response)} songs in playlist {playlist_id}")
        return songs_response
