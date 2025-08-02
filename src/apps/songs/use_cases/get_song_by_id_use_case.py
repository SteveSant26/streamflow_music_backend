from typing import Any

from apps.songs.domain.exceptions import SongNotFoundException
from common.interfaces.ibase_use_case import BaseGetByIdUseCase

from ..domain.entities import SongEntity
from ..domain.repository import ISongRepository


class GetSongByIdUseCase(BaseGetByIdUseCase[SongEntity, Any]):
    """Caso de uso para obtener una canción por ID"""

    def __init__(self, repository: ISongRepository):
        super().__init__(repository)

    def _get_not_found_exception(self, entity_id: str) -> Exception:
        return SongNotFoundException(entity_id)
