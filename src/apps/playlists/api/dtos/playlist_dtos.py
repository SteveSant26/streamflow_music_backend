from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class PlaylistResponseDTO:
    """DTO para respuestas de playlist"""

    id: str
    name: str
    description: Optional[str] = None
    user_id: str = ""
    is_default: bool = False
    is_public: bool = False
    song_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PlaylistSongResponseDTO:
    """DTO para respuestas de canción en playlist"""

    id: str
    playlist_id: str
    song_id: str
    position: int
    added_at: Optional[datetime] = None
    # Datos de la canción (opcional)
    song_title: Optional[str] = None
    song_artist: Optional[str] = None
    song_duration: Optional[int] = None


@dataclass
class CreatePlaylistRequestDTO:
    """DTO para crear playlist"""

    name: str
    description: Optional[str] = None
    is_public: bool = False
    user_id: str = ""


@dataclass
class UpdatePlaylistRequestDTO:
    """DTO para actualizar playlist"""

    playlist_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


@dataclass
class AddSongToPlaylistRequestDTO:
    """DTO para añadir canción a playlist"""

    playlist_id: str
    song_id: str
    position: Optional[int] = None


@dataclass
class RemoveSongFromPlaylistRequestDTO:
    """DTO para remover canción de playlist"""

    playlist_id: str
    song_id: str


@dataclass
class SearchPlaylistsRequestDTO:
    """DTO para búsqueda de playlists"""

    query: str
    user_id: Optional[str] = None
    limit: int = 20


@dataclass
class GetPublicPlaylistsRequestDTO:
    """DTO para obtener playlists públicas"""

    limit: int = 20
    offset: int = 0


@dataclass
class ReorderPlaylistSongsRequestDTO:
    """DTO para reordenar canciones en playlist"""

    playlist_id: str
    song_positions: List[tuple[str, int]]  # Lista de (song_id, nueva_posición)
