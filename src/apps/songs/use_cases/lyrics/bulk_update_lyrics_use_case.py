from common.adapters.lyrics import LyricsUpdateService
from common.mixins.logging_mixin import LoggingMixin

from ...infrastructure.models.song_model import SongModel


class BulkUpdateLyricsUseCase(LoggingMixin):
    """Use case para actualizar letras de múltiples canciones"""

    def __init__(self):
        super().__init__()
        self.lyrics_update_service = LyricsUpdateService()

    async def execute(
        self, limit: int = 50, only_without_lyrics: bool = True, max_concurrent: int = 3
    ) -> dict:
        """
        Actualiza letras para múltiples canciones.
        """
        try:
            queryset = SongModel.objects.select_related("artist").order_by(
                "-play_count"
            )
            if only_without_lyrics:
                queryset = queryset.filter(lyrics__isnull=True)
            queryset = queryset[:limit]
            self.logger.info(
                f"Iniciando actualización masiva de letras para {limit} canciones"
            )
            stats = await self.lyrics_update_service.bulk_update_lyrics(
                queryset, max_concurrent=max_concurrent
            )
            return stats
        except Exception as e:
            self.logger.error(f"Error en actualización masiva de letras: {str(e)}")
            return {
                "total_processed": 0,
                "updated": 0,
                "errors": 1,
                "skipped": 0,
                "error_message": str(e),
            }
