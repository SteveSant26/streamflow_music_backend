from apps.songs.domain.exceptions import SongNotFoundException
from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.entities import SongEntity
from ..domain.repository.Isong_repository import ISongRepository


class GetSongByIdUseCase(BaseUseCase[str, SongEntity]):
    """Caso de uso para obtener una canción por ID"""

    def __init__(self, repository: ISongRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=1.0)  # Consulta simple por ID
    async def execute(self, song_id: str) -> SongEntity:
        """
        Obtiene una canción por ID

        Args:
            song_id: ID de la canción

        Returns:
            Entidad de canción encontrada

        Raises:
            SongNotFoundException: Si la canción no existe
        """
        self.logger.debug(f"Getting song with ID: {song_id}")
        song = await self.repository.get_by_id(song_id)

        if not song:
            self.logger.warning(f"Song not found with ID: {song_id}")
            raise SongNotFoundException(song_id)

        self.logger.info(f"Successfully retrieved song: {song_id}")
        return song
