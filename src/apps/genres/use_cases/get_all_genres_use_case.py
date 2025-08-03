"""
Caso de uso para obtener todos los géneros.
"""

from typing import Any

from common.interfaces.ibase_use_case import BaseGetAllUseCase

from ..domain.entities import GenreEntity
from ..domain.repository import IGenreRepository


class GetAllGenresUseCase(BaseGetAllUseCase[GenreEntity, Any]):
    """Caso de uso para obtener todos los géneros"""

    def __init__(self, repository: IGenreRepository):
        super().__init__(repository)
