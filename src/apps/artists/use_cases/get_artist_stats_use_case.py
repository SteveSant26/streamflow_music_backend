from typing import Any, Dict

from common.interfaces.ibase_use_case import BaseUseCase
from common.utils.logging_decorators import log_execution, log_performance

from ..domain.repository import IArtistRepository


class GetArtistStatsUseCase(BaseUseCase[None, Dict[str, Any]]):
    """Caso de uso para obtener estadísticas de artistas"""

    def __init__(self, repository: IArtistRepository):
        super().__init__()
        self.repository = repository

    @log_execution(include_args=True, include_result=False, log_level="DEBUG")
    @log_performance(threshold_seconds=2.0)
    async def execute(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de artistas

        Returns:
            Diccionario con estadísticas de artistas
        """
        self.logger.debug("Getting artist statistics")
        all_artists = await self.repository.get_all()

        stats = {
            "total_artists": len(all_artists),
            "verified_artists": len([a for a in all_artists if a.is_verified]),
            "total_followers": sum(a.followers_count for a in all_artists),
        }

        # Estadísticas por país
        countries: Dict[str, int] = {}
        for artist in all_artists:
            if artist.country:
                countries[artist.country] = countries.get(artist.country, 0) + 1

        stats["artists_by_country"] = len(countries)
        stats["top_country"] = (  # type: ignore
            max(countries.items(), key=lambda x: x[1])[0] if countries else None
        )

        self.logger.info("Artist statistics generated successfully")
        return stats
