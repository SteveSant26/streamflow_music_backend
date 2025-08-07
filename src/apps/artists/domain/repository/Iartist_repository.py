from abc import abstractmethod
from typing import Any, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import ArtistEntity


class IArtistRepository(IBaseRepository[ArtistEntity, Any]):
    """Interface del repositorio de artistas"""

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[ArtistEntity]:
        """Busca un artista por nombre exacto"""
<<<<<<< HEAD

    @abstractmethod
    async def search_by_name(self, name: str, limit: int = 10) -> List[ArtistEntity]:
        """Busca artistas por nombre (búsqueda parcial)"""

    @abstractmethod
    async def find_by_country(
        self, country: str, limit: int = 10
    ) -> List[ArtistEntity]:
        """Busca artistas por país"""

    @abstractmethod
    async def get_popular_artists(self, limit: int = 10) -> List[ArtistEntity]:
        """Obtiene los artistas más populares"""

    @abstractmethod
    async def get_verified_artists(self, limit: int = 10) -> List[ArtistEntity]:
        """Obtiene artistas verificados"""

    @abstractmethod
    async def find_or_create_by_name(
        self, name: str, image_url: Optional[str] = None
    ) -> ArtistEntity:
        """Busca un artista por nombre, si no existe lo crea"""

    @abstractmethod
    async def get_by_source(
        self, source_type: str, source_id: str
    ) -> Optional[ArtistEntity]:
        """Busca un artista por fuente externa (YouTube channel, etc.)"""
=======
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
