from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class PlaylistCreateRequestDTO:
    """DTO para crear una nueva playlist"""
    name: str
    description: Optional[str] = None
    is_public: bool = False


@dataclass
class PlaylistUpdateRequestDTO:
    """DTO para actualizar una playlist"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


@dataclass
class PlaylistSongResponseDTO:
    """DTO para una canción dentro de una playlist"""
    id: UUID
    title: str
    artist_name: Optional[str]
    album_name: Optional[str]
    duration_seconds: int
    thumbnail_url: Optional[str]
    position: int
    added_at: datetime


@dataclass
class PlaylistResponseDTO:
    """DTO para respuesta de playlist"""
    id: UUID
    name: str
    description: Optional[str]
    user_id: UUID
    is_default: bool
    is_public: bool
    total_songs: int
    created_at: datetime
    updated_at: Optional[datetime]
    songs: Optional[List[PlaylistSongResponseDTO]] = None


@dataclass
class AddSongToPlaylistRequestDTO:
    """DTO para agregar una canción a una playlist"""
    song_id: UUID
    position: Optional[int] = None  # Si no se especifica, se agrega al final


@dataclass
class RemoveSongFromPlaylistRequestDTO:
    """DTO para remover una canción de una playlist"""
    song_id: UUID


@dataclass
class ReorderPlaylistSongsRequestDTO:
    """DTO para reordenar canciones en una playlist"""
    song_positions: List[dict]  # Lista de {"song_id": UUID, "position": int}
