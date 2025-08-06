from typing import Optional

from django.core.exceptions import ObjectDoesNotExist

from ...common.adapters.lyrics.lyrics_service import LyricsService, LyricsUpdateService
from ...common.mixins.logging_mixin import LoggingMixin
from ..infrastructure.models.song_model import SongModel


class GetSongLyricsUseCase(LoggingMixin):
    """Use case para obtener letras de una canción"""

    def __init__(self):
        super().__init__()
        self.lyrics_service = LyricsService()
        self.lyrics_update_service = LyricsUpdateService()

    async def execute(self, song_id: str, fetch_if_missing: bool = True) -> Optional[str]:
        """
        Obtiene las letras de una canción.
        
        Args:
            song_id: ID de la canción
            fetch_if_missing: Si es True, intenta buscar letras si no existen
            
        Returns:
            str: Letras de la canción o None si no se encuentran
        """
        try:
            song = await SongModel.objects.select_related('artist').aget(id=song_id)
            
            # Si ya tiene letras, devolverlas
            if song.lyrics:
                self.logger.debug(f"Letras encontradas en BD para: {song.title}")
                return song.lyrics
            
            # Si no tiene letras y se solicita buscarlas
            if fetch_if_missing:
                self.logger.info(f"Buscando letras para: {song.title}")
                
                lyrics = await self.lyrics_service.get_lyrics(
                    title=song.title,
                    artist=song.artist.name if song.artist else "Unknown Artist",
                    youtube_id=song.source_id if song.source_type == 'youtube' else None
                )
                
                if lyrics:
                    # Guardar las letras encontradas
                    song.lyrics = lyrics
                    await song.asave(update_fields=['lyrics'])
                    self.logger.info(f"Letras guardadas para: {song.title}")
                    return lyrics
                else:
                    self.logger.warning(f"No se encontraron letras para: {song.title}")
                    return None
            
            return None
            
        except ObjectDoesNotExist:
            self.logger.error(f"Canción con ID {song_id} no encontrada")
            return None
        except Exception as e:
            self.logger.error(f"Error obteniendo letras para canción {song_id}: {str(e)}")
            return None


class UpdateSongLyricsUseCase(LoggingMixin):
    """Use case para actualizar letras de una canción específica"""

    def __init__(self):
        super().__init__()
        self.lyrics_update_service = LyricsUpdateService()

    async def execute(self, song_id: str, force_update: bool = False) -> bool:
        """
        Actualiza las letras de una canción específica.
        
        Args:
            song_id: ID de la canción
            force_update: Si es True, actualiza incluso si ya tiene letras
            
        Returns:
            bool: True si se actualizaron las letras, False en caso contrario
        """
        try:
            song = await SongModel.objects.select_related('artist').aget(id=song_id)
            
            # Si ya tiene letras y no se fuerza la actualización
            if song.lyrics and not force_update:
                self.logger.debug(f"La canción '{song.title}' ya tiene letras")
                return False
            
            # Actualizar letras
            return await self.lyrics_update_service.update_song_lyrics(song)
            
        except ObjectDoesNotExist:
            self.logger.error(f"Canción con ID {song_id} no encontrada")
            return False
        except Exception as e:
            self.logger.error(f"Error actualizando letras para canción {song_id}: {str(e)}")
            return False


class BulkUpdateLyricsUseCase(LoggingMixin):
    """Use case para actualizar letras de múltiples canciones"""

    def __init__(self):
        super().__init__()
        self.lyrics_update_service = LyricsUpdateService()

    async def execute(
        self, 
        limit: int = 50, 
        only_without_lyrics: bool = True,
        max_concurrent: int = 3
    ) -> dict:
        """
        Actualiza letras para múltiples canciones.
        
        Args:
            limit: Número máximo de canciones a procesar
            only_without_lyrics: Si es True, solo procesa canciones sin letras
            max_concurrent: Número máximo de actualizaciones concurrentes
            
        Returns:
            dict: Estadísticas de la actualización
        """
        try:
            # Construir query
            queryset = SongModel.objects.select_related('artist').order_by('-play_count')
            
            if only_without_lyrics:
                queryset = queryset.filter(lyrics__isnull=True)
            
            queryset = queryset[:limit]
            
            self.logger.info(f"Iniciando actualización masiva de letras para {limit} canciones")
            
            # Ejecutar actualización masiva
            stats = await self.lyrics_update_service.bulk_update_lyrics(
                queryset, 
                max_concurrent=max_concurrent
            )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error en actualización masiva de letras: {str(e)}")
            return {
                'total_processed': 0,
                'updated': 0,
                'errors': 1,
                'skipped': 0,
                'error_message': str(e)
            }
