from typing import Any

from common.interfaces.ibase_use_case import BaseGetAllUseCase

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetAllArtistsUseCase(BaseGetAllUseCase[ArtistEntity, Any]):
    """Caso de uso para obtener todos los artistas"""

    def __init__(self, repository: IArtistRepository):
        super().__init__(repository)
