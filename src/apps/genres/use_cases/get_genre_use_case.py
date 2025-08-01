from common.interfaces.ibase_use_case import BaseGetByIdUseCase

from ..domain.entities import GenreEntity
from ..domain.repository import IGenreRepository


class GetGenreUseCase(BaseGetByIdUseCase[GenreEntity]):
    """Caso de uso para obtener un género por ID"""

    def __init__(self, repository: IGenreRepository):
        super().__init__(repository)
