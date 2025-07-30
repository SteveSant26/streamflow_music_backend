from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, date


@dataclass
class GenreEntity:
    """Entidad que representa un género musical"""
    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    song_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class ArtistEntity:
    """Entidad que representa un artista"""
    id: str
    name: str
    biography: Optional[str] = None
    country: Optional[str] = None
    image_url: Optional[str] = None
    followers_count: int = 0
    is_verified: bool = False
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AlbumEntity:
    """Entidad que representa un álbum"""
    id: str
    title: str
    artist_id: str
    artist_name: Optional[str] = None  # Para evitar joins constantes
    release_date: Optional[date] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    total_tracks: int = 0
    play_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SongEntity:
    """Entidad que representa una canción"""
    id: str
    title: str
    artist_id: str
    duration_seconds: int
    artist_name: Optional[str] = None
    album_id: Optional[str] = None
    album_title: Optional[str] = None
    file_url: Optional[str] = None  # URL del archivo de audio
    lyrics: Optional[str] = None
    track_number: Optional[int] = None
    genre_id: Optional[str] = None
    genre_name: Optional[str] = None
    play_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SearchResultEntity:
    """Entidad que representa resultados de búsqueda"""
    query: str
    songs: List[dict]
    artists: List[dict]
    albums: List[dict]
    genres: List[dict]
    total_results: int


@dataclass
class PaginatedResultEntity:
    """Entidad para resultados paginados"""
    results: List[dict]  # Puede ser songs, artists, albums
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool
