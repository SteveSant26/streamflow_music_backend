from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional


@dataclass
class AlbumResponseDTO:
    """DTO para respuestas de álbum"""

    id: str
    title: str
    artist_id: str
    artist_name: Optional[str] = None
    release_date: Optional[date] = None
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    total_tracks: int = 0
    play_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AlbumSearchRequestDTO:
    """DTO para búsqueda de álbumes"""

    q: str
    artist_id: Optional[str] = None
    artist_name: Optional[str] = None
    limit: int = 10


@dataclass
class AlbumSearchResponseDTO:
    """DTO para respuesta de búsqueda de álbumes"""

    source: str  # "local_cache", "youtube_api", "not_found"
    results: list
    message: Optional[str] = None


@dataclass
class SearchAlbumsByTitleRequestDTO:
    """DTO para búsqueda de álbumes por título"""

    title: str
    limit: int = 10


@dataclass
class SaveAlbumRequestDTO:
    """DTO para guardar un álbum desde fuentes externas"""

    title: str
    artist_id: str
    artist_name: str
    cover_image_url: Optional[str] = None
    source_type: str = "manual"
    source_id: Optional[str] = None
    source_url: Optional[str] = None
    description: Optional[str] = None
    release_date: Optional[date] = None


@dataclass
class SaveAlbumResponseDTO:
    """DTO de respuesta para guardar un álbum"""

    id: str
    title: str
    artist_id: str
    artist_name: str
    cover_image_url: Optional[str] = None
    source_type: str = "manual"
    source_id: Optional[str] = None
    was_created: bool = False  # Indica si fue creado o ya existía


@dataclass
class GetAlbumsByArtistRequestDTO:
    """DTO para obtener álbumes por artista"""

    artist_id: str
    limit: int = 10


@dataclass
class GetPopularAlbumsRequestDTO:
    """DTO para obtener álbumes populares"""

    limit: int = 10
