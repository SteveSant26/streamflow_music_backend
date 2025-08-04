from apps.artists.domain.exceptions import ArtistNotFoundException
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import ArtistEntity
from ..domain.repository import IArtistRepository


class GetArtistByNameUseCase(BaseUseCase[str, ArtistEntity]):
    """Caso de uso para obtener un artista por nombre exacto"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)
    async def execute(self, name: str) -> ArtistEntity:
        """
        Obtiene un artista por nombre exacto

        Args:
            name: Nombre exacto del artista

        Returns:
            Entidad del artista encontrado

        Raises:
            ArtistNotFoundException: Si el artista no existe
        """
        self.logger.debug(f"Getting artist by name: {name}")
        artist = await self.repository.find_by_name(name)

        if not artist:
            self.logger.warning(f"Artist not found with name: {name}")
            raise ArtistNotFoundException(name)

        self.logger.info(f"Successfully retrieved artist: {name}")
        return artist
