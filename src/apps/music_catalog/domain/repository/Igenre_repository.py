from abc import abstractmethod
from typing import TYPE_CHECKING, List

from apps.music_catalog.infrastructure.models.genre import GenreModel
from common.interfaces import IBaseRepository

from ..entities import GenreEntity

if TYPE_CHECKING:
    pass


class IGenreRepository(IBaseRepository[GenreEntity, GenreModel]):
    """Interface para el repositorio de géneros"""

    @abstractmethod
    def get_active_genres(self) -> List[GenreEntity]:
        """Obtiene géneros activos"""

    @abstractmethod
    def search_by_name(self, name: str) -> List[GenreEntity]:
        """Busca géneros por nombre"""
