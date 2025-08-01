from apps.artists.domain.exceptions import ArtistNotFoundException
from common.interfaces.ibase_use_case import (
    BaseGetAllUseCase,
    BaseGetByIdUseCase,
    BaseUseCase,
)
from common.utils.logging_decorators import log_execution

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetArtistUseCase(BaseGetByIdUseCase[ArtistEntity]):
    """Caso de uso para obtener un artista por ID"""

    def __init__(self, repository: IArtistRepository):
        super().__init__(repository)

    def _get_not_found_exception(self, entity_id: str) -> Exception:
        return ArtistNotFoundException(entity_id)


class GetAllArtistsUseCase(BaseGetAllUseCase[ArtistEntity]):
    """Caso de uso para obtener todos los artistas"""

    def __init__(self, repository: IArtistRepository):
        super().__init__(repository)


class SearchArtistsByNameUseCase(BaseUseCase[str, list[ArtistEntity]]):
    """Caso de uso para buscar artistas por nombre"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, name: str, limit: int = 10) -> list[ArtistEntity]:
        """
        Busca artistas por nombre

        Args:
            name: Nombre del artista a buscar
            limit: Límite de resultados

        Returns:
            Lista de artistas encontrados
        """
        self.logger.info(f"Searching artists by name: {name}")
        return self.repository.search_by_name(name, limit)


class GetArtistsByCountryUseCase(BaseUseCase[str, list[ArtistEntity]]):
    """Caso de uso para obtener artistas por país"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, country: str, limit: int = 10) -> list[ArtistEntity]:
        """
        Obtiene artistas por país

        Args:
            country: País del artista
            limit: Límite de resultados

        Returns:
            Lista de artistas del país especificado
        """
        self.logger.info(f"Getting artists by country: {country}")
        return self.repository.find_by_country(country, limit)


class GetPopularArtistsUseCase(BaseUseCase[None, list[ArtistEntity]]):
    """Caso de uso para obtener artistas populares"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, limit: int = 10) -> list[ArtistEntity]:
        """
        Obtiene artistas populares ordenados por seguidores

        Args:
            limit: Límite de resultados

        Returns:
            Lista de artistas populares
        """
        self.logger.info(f"Getting popular artists with limit: {limit}")
        return self.repository.get_popular_artists(limit)


class GetVerifiedArtistsUseCase(BaseUseCase[None, list[ArtistEntity]]):
    """Caso de uso para obtener artistas verificados"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    def execute(self, limit: int = 10) -> list[ArtistEntity]:
        """
        Obtiene artistas verificados

        Args:
            limit: Límite de resultados

        Returns:
            Lista de artistas verificados
        """
        self.logger.info(f"Getting verified artists with limit: {limit}")
        return self.repository.get_verified_artists(limit)
