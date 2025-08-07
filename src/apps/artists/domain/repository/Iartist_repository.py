from abc import abstractmethod
from typing import Any, Optional

from common.interfaces.ibase_repository import IBaseRepository

from ..entities import ArtistEntity


class IArtistRepository(IBaseRepository[ArtistEntity, Any]):
    """Interface del repositorio de artistas"""

    @abstractmethod
    async def find_by_name(self, name: str) -> Optional[ArtistEntity]:
        """Busca un artista por nombre exacto"""
