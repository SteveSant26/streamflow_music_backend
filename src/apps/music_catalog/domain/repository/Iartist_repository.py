from abc import abstractmethod
from typing import List

from apps.music_catalog.infrastructure.models.artist import ArtistModel
from common.interfaces import IBaseRepository

from ..entities import ArtistEntity


class IArtistRepository(IBaseRepository[ArtistEntity, ArtistModel]):
    """Interface para el repositorio de artistas"""

    @abstractmethod
    def search_by_name(self, name: str) -> List[ArtistEntity]:
        """Busca artistas por nombre"""

    @abstractmethod
    def get_by_country(self, country: str) -> List[ArtistEntity]:
        """Obtiene artistas por país"""

    @abstractmethod
    def get_popular_artists(self, limit: int = 50) -> List[ArtistEntity]:
        """Obtiene artistas populares"""
