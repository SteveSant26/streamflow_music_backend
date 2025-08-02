"""
Caso de uso para obtener todos los géneros.
"""

from common.interfaces.ibase_use_case import BaseGetAllUseCase

from ..domain.entities import GenreEntity
from ..domain.repository.Igenre_repository import IGenreRepository


class GetAllGenresUseCase(BaseGetAllUseCase[GenreEntity]):
    """Caso de uso para obtener todos los géneros"""

    def __init__(self, repository: IGenreRepository):
        super().__init__(repository)
