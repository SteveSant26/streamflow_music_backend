"""
Caso de uso para obtener un género específico.
"""

from common.interfaces.ibase_use_case import BaseGetByIdUseCase

from ..domain.entities import GenreEntity
from ..domain.exceptions import GenreNotFoundException
from ..domain.repository.Igenre_repository import IGenreRepository


class GetGenreUseCase(BaseGetByIdUseCase[GenreEntity]):
    """Caso de uso para obtener un género específico"""

    def __init__(self, repository: IGenreRepository):
        super().__init__(repository)

    def _get_not_found_exception(self, entity_id: str) -> Exception:
        return GenreNotFoundException(entity_id)
