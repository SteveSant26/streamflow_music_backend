from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class SongResponseDTO:
    """DTO para respuestas de canción"""

    id: str
    title: str
    album_id: Optional[str] = None
    artist_id: Optional[str] = None
    genre_id: Optional[str] = None
    duration_seconds: int = 0
    album_title: Optional[str] = None
    artist_name: Optional[str] = None
    genre_name: Optional[str] = None
    track_number: Optional[int] = None
    file_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    lyrics: Optional[str] = None
    tags: Optional[List[str]] = None
    play_count: int = 0
    favorite_count: int = 0
    download_count: int = 0
    source_type: Optional[str] = None
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    is_active: bool = True
    audio_quality: Optional[str] = None
    created_at: Optional[datetime] = None
    release_date: Optional[datetime] = None
    audio_downloaded: bool = False  # Indica si el audio está descargado

    # Campos adicionales para compatibilidad con serializers
    youtube_video_id: Optional[str] = None  # source_id para videos de YouTube
    youtube_url: Optional[str] = None  # source_url para videos de YouTube
    youtube_view_count: int = 0  # Conteo de views en YouTube
    youtube_like_count: int = 0  # Conteo de likes en YouTube
    is_explicit: bool = False  # Indica si el contenido es explícito
    published_at: Optional[datetime] = None  # Fecha de publicación original


@dataclass
class SongSearchRequestDTO:
    """DTO para búsqueda de canciones"""

    query: str
    limit: int = 20
    include_youtube: bool = True


@dataclass
class SongSearchResponseDTO:
    """DTO para respuesta de búsqueda de canciones"""

    source: str  # "local_cache", "youtube_api", "mixed"
    results: list
    total_found: int
    message: Optional[str] = None


@dataclass
class RandomSongsRequestDTO:
    """DTO para solicitud de canciones aleatorias"""

    count: int = 6
    force_refresh: bool = False


@dataclass
class IncrementCountRequestDTO:
    """DTO para incrementar contadores"""

    song_id: str
