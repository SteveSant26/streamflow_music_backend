from typing import Any

from apps.albums.domain.exceptions import AlbumNotFoundException
from common.interfaces.ibase_use_case import BaseGetByIdUseCase

from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class GetAlbumUseCase(BaseGetByIdUseCase[AlbumEntity, Any]):
    """Caso de uso para obtener un álbum por ID"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__(repository)

    def _get_not_found_exception(self, entity_id: str) -> Exception:
        return AlbumNotFoundException(entity_id)
