from dataclasses import dataclass
from typing import List


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
