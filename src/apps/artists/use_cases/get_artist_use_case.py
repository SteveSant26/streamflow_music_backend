from apps.artists.domain.exceptions import ArtistNotFoundException
from common.interfaces.ibase_use_case import BaseGetByIdUseCase

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetArtistUseCase(BaseGetByIdUseCase[ArtistEntity]):
    """Caso de uso para obtener un artista por ID"""

    def __init__(self, repository: IArtistRepository):
        super().__init__(repository)

    def _get_not_found_exception(self, entity_id: str) -> Exception:
        return ArtistNotFoundException(entity_id)
