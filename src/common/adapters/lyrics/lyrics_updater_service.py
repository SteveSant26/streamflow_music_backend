import asyncio

from ...mixins.logging_mixin import LoggingMixin
from .lyrics_service import LyricsService


class LyricsUpdateService(LoggingMixin):
    """Servicio para actualizar letras de canciones existentes"""

    def __init__(self):
        super().__init__()
        self.lyrics_service = LyricsService()

    async def update_song_lyrics(self, song_model):
        """
        Actualiza las letras de una canción específica si no las tiene.

        Args:
            song_model: Instancia del modelo SongModel

        Returns:
            bool: True si se actualizaron las letras, False en caso contrario
        """
        if song_model.lyrics:
            self.logger.debug(f"La canción '{song_model.title}' ya tiene letras")
            return False

        try:
            lyrics = await self.lyrics_service.get_lyrics(
                title=song_model.title,
                artist=song_model.artist.name if song_model.artist else "Unknown",
                youtube_id=(
                    song_model.source_id
                    if song_model.source_type == "youtube"
                    else None
                ),
            )

            if lyrics:
                song_model.lyrics = lyrics
                await song_model.asave(update_fields=["lyrics"])
                self.logger.info(f"Letras actualizadas para: {song_model.title}")
                return True
            else:
                self.logger.debug(f"No se encontraron letras para: {song_model.title}")
                return False

        except Exception as e:
            self.logger.error(
                f"Error actualizando letras para {song_model.title}: {str(e)}"
            )
            return False

    async def bulk_update_lyrics(self, song_queryset, max_concurrent=3):
        """
        Actualiza letras para múltiples canciones en paralelo.

        Args:
            song_queryset: QuerySet de canciones
            max_concurrent: Máximo número de actualizaciones concurrentes

        Returns:
            dict: Estadísticas de la actualización
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def update_single_song(song):
            async with semaphore:
                return await self.update_song_lyrics(song)

        tasks = [update_single_song(song) async for song in song_queryset]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Calcular estadísticas
        updated = sum(1 for result in results if result is True)
        errors = sum(1 for result in results if isinstance(result, Exception))
        total = len(results)

        stats = {
            "total_processed": total,
            "updated": updated,
            "errors": errors,
            "skipped": total - updated - errors,
        }

        self.logger.info(f"Actualización masiva completada: {stats}")
        return stats
