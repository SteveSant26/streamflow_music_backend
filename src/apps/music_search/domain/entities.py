from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class SearchResultEntity:
    """Entidad que representa un resultado de búsqueda"""

    result_type: str  # "artist", "album", "song", "genre"
    result_id: str
    title: str
    subtitle: Optional[str] = None  # artist para songs/albums, etc.
    image_url: Optional[str] = None
    relevance_score: float = 0.0


@dataclass
class SearchQueryEntity:
    """Entidad que representa una consulta de búsqueda"""

    id: str
    query_text: str
    user_id: Optional[str] = None
    filters: Optional[dict] = None  # filtros aplicados
    results_count: int = 0
    created_at: Optional[datetime] = None


@dataclass
class SearchResponseEntity:
    """Entidad que representa la respuesta completa de búsqueda"""

    query: str
    artists: List[SearchResultEntity]
    albums: List[SearchResultEntity]
    songs: List[SearchResultEntity]
    genres: List[SearchResultEntity]
    total_results: int
    search_time_ms: Optional[float] = None
