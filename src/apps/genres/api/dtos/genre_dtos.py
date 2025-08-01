from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class GenreResponseDTO:
    """DTO para respuestas de género"""

    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    color_hex: Optional[str] = None
    popularity_score: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class GenreSearchRequestDTO:
    """DTO para búsqueda de géneros"""

    name: str
    limit: int = 10


@dataclass
class PopularGenresRequestDTO:
    """DTO para solicitud de géneros populares"""

    limit: int = 10


@dataclass
class SearchGenresRequestDTO:
    """DTO para búsqueda de géneros"""

    query: str
    limit: int = 10
