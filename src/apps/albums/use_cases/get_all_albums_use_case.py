from typing import Any

from common.interfaces.ibase_use_case import BaseGetAllUseCase

from ..domain.entities import AlbumEntity
from ..domain.repository import IAlbumRepository


class GetAllAlbumsUseCase(BaseGetAllUseCase[AlbumEntity, Any]):
    """Caso de uso para obtener todos los álbumes"""

    def __init__(self, repository: IAlbumRepository):
        super().__init__(repository)
