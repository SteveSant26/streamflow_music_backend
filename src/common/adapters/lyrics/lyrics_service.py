import asyncio
import re
import time
from typing import Dict, List, Optional, Tuple

import aiohttp
import requests
from django.conf import settings

from ...mixins.logging_mixin import LoggingMixin
from ...utils.retry_manager import RetryManager
from ...utils.validators import TextCleaner


class LyricsService(LoggingMixin):
    """
    Servicio para obtener letras de canciones desde múltiples fuentes.
    
    Fuentes soportadas:
    1. YouTube (usando yt-dlp para obtener subtítulos/letras)
    2. Lyrics.ovh API (gratis)
    3. AZLyrics web scraping (como respaldo)
    4. Genius API (opcional, requiere API key)
    """

    def __init__(self):
        super().__init__()
        self.text_cleaner = TextCleaner()
        self.retry_manager = RetryManager(max_retries=3, base_delay=1.0)
        
        # Rate limiting
        self.last_request_time = {}
        self.rate_limits = {
            'lyrics_ovh': 1.0,  # 1 segundo entre requests
            'azlyrics': 2.0,    # 2 segundos entre requests
            'genius': 0.5,      # 0.5 segundos entre requests
        }
        
        # Genius API (opcional)
        self.genius_api_key = getattr(settings, 'GENIUS_API_KEY', None)
        
    async def get_lyrics(
        self, 
        title: str, 
        artist: str, 
        youtube_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Obtiene las letras de una canción usando múltiples fuentes.
        
        Args:
            title: Título de la canción
            artist: Nombre del artista
            youtube_id: ID del video de YouTube (opcional)
            
        Returns:
            str: Letras de la canción o None si no se encuentran
        """
        self.logger.info(f"Buscando letras para: {artist} - {title}")
        
        # Limpiar y normalizar los datos de entrada
        clean_title = self.text_cleaner.clean_title(title)
        clean_artist = self.text_cleaner.clean_title(artist)
        
        # Intentar diferentes fuentes en orden de preferencia
        sources = [
            ('youtube', self._get_lyrics_from_youtube),
            ('lyrics_ovh', self._get_lyrics_from_lyrics_ovh),
            ('genius', self._get_lyrics_from_genius),
            ('azlyrics', self._get_lyrics_from_azlyrics),
        ]
        
        for source_name, source_func in sources:
            try:
                self.logger.debug(f"Intentando obtener letras desde {source_name}")
                
                if source_name == 'youtube' and youtube_id:
                    lyrics = await source_func(youtube_id, clean_title, clean_artist)
                elif source_name == 'genius' and not self.genius_api_key:
                    continue  # Skip Genius si no hay API key
                else:
                    lyrics = await source_func(clean_title, clean_artist)
                
                if lyrics and self._validate_lyrics(lyrics):
                    self.logger.info(f"Letras encontradas desde {source_name}")
                    return self._format_lyrics(lyrics)
                    
            except Exception as e:
                self.logger.warning(f"Error obteniendo letras desde {source_name}: {str(e)}")
                continue
        
        self.logger.warning(f"No se pudieron encontrar letras para: {artist} - {title}")
        return None
    
    async def _get_lyrics_from_youtube(
        self, 
        youtube_id: str, 
        title: str, 
        artist: str
    ) -> Optional[str]:
        """Intenta obtener letras desde YouTube usando yt-dlp"""
        try:
            import yt_dlp
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'skip_download': True,
            }
            
            url = f"https://www.youtube.com/watch?v={youtube_id}"
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Buscar en el título o descripción indicios de letras
                description = info.get('description', '').lower()
                video_title = info.get('title', '').lower()
                
                # Verificar si es un video de letras
                lyrics_indicators = ['lyrics', 'letra', 'lyric video', 'official lyrics']
                is_lyrics_video = any(indicator in video_title for indicator in lyrics_indicators)
                
                if is_lyrics_video and description:
                    # Extraer letras de la descripción si parece ser un video de letras
                    lyrics = self._extract_lyrics_from_description(description)
                    if lyrics:
                        return lyrics
                        
                # Intentar obtener subtítulos
                if info.get('subtitles') or info.get('automatic_captions'):
                    return await self._extract_lyrics_from_captions(info)
                    
        except Exception as e:
            self.logger.debug(f"Error obteniendo letras de YouTube: {str(e)}")
            
        return None
    
    async def _get_lyrics_from_lyrics_ovh(self, title: str, artist: str) -> Optional[str]:
        """Obtiene letras desde lyrics.ovh API (gratis)"""
        await self._rate_limit('lyrics_ovh')
        
        url = f"https://api.lyrics.ovh/v1/{artist}/{title}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        lyrics = data.get('lyrics')
                        if lyrics:
                            return lyrics.strip()
        except Exception as e:
            self.logger.debug(f"Error obteniendo letras de lyrics.ovh: {str(e)}")
            
        return None
    
    async def _get_lyrics_from_genius(self, title: str, artist: str) -> Optional[str]:
        """Obtiene letras desde Genius API (requiere API key)"""
        if not self.genius_api_key:
            return None
            
        await self._rate_limit('genius')
        
        try:
            # Buscar la canción
            search_url = "https://api.genius.com/search"
            headers = {"Authorization": f"Bearer {self.genius_api_key}"}
            params = {"q": f"{artist} {title}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, headers=headers, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        hits = data.get('response', {}).get('hits', [])
                        
                        if hits:
                            song_url = hits[0]['result']['url']
                            # Nota: Genius API no proporciona letras directamente
                            # Necesitaríamos scraping adicional del HTML
                            return await self._scrape_genius_lyrics(song_url)
                            
        except Exception as e:
            self.logger.debug(f"Error obteniendo letras de Genius: {str(e)}")
            
        return None
    
    async def _get_lyrics_from_azlyrics(self, title: str, artist: str) -> Optional[str]:
        """Obtiene letras desde AZLyrics mediante web scraping"""
        await self._rate_limit('azlyrics')
        
        try:
            # Formatear para URL de AZLyrics
            artist_clean = re.sub(r'[^a-z0-9]', '', artist.lower())
            title_clean = re.sub(r'[^a-z0-9]', '', title.lower())
            
            url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{title_clean}.html"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._extract_azlyrics_content(html)
                        
        except Exception as e:
            self.logger.debug(f"Error obteniendo letras de AZLyrics: {str(e)}")
            
        return None
    
    def _extract_lyrics_from_description(self, description: str) -> Optional[str]:
        """Extrae letras de la descripción de un video de YouTube"""
        try:
            # Buscar patrones comunes de letras en descripciones
            lines = description.split('\n')
            
            # Filtrar líneas que parecen ser letras
            lyrics_lines = []
            for line in lines:
                line = line.strip()
                if line and not self._is_metadata_line(line):
                    lyrics_lines.append(line)
            
            if len(lyrics_lines) > 5:  # Al menos 5 líneas para considerar como letras
                return '\n'.join(lyrics_lines[:50])  # Limitar a 50 líneas
                
        except Exception:
            pass
            
        return None
    
    def _is_metadata_line(self, line: str) -> bool:
        """Determina si una línea es metadata y no parte de las letras"""
        metadata_patterns = [
            r'^https?://',  # URLs
            r'©|\(c\)',     # Copyright
            r'follow|subscribe|like',  # Social media
            r'produced by|written by|composed by',  # Credits
            r'album:|single:|ep:',  # Album info
            r'release date|released',  # Release info
        ]
        
        line_lower = line.lower()
        return any(re.search(pattern, line_lower) for pattern in metadata_patterns)
    
    async def _extract_lyrics_from_captions(self, video_info: Dict) -> Optional[str]:
        """Extrae letras de los subtítulos/captions de YouTube"""
        # Esta implementación requeriría procesamiento adicional de subtítulos
        # Por ahora retorna None, pero se puede implementar más tarde
        return None
    
    async def _scrape_genius_lyrics(self, url: str) -> Optional[str]:
        """Hace scraping de letras desde una página de Genius"""
        # Implementación simplificada - en producción usar BeautifulSoup
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                async with session.get(url, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Extraer letras usando regex simple (mejorar con BeautifulSoup)
                        lyrics_match = re.search(r'<div[^>]*lyrics[^>]*>(.*?)</div>', html, re.DOTALL)
                        if lyrics_match:
                            return self._clean_html(lyrics_match.group(1))
        except Exception:
            pass
        return None
    
    def _extract_azlyrics_content(self, html: str) -> Optional[str]:
        """Extrae letras del HTML de AZLyrics"""
        try:
            # AZLyrics tiene las letras en un div específico
            lyrics_match = re.search(
                r'<!-- Usage of azlyrics\.com content.*?-->(.*?)<!-- MxM banner -->',
                html,
                re.DOTALL
            )
            
            if lyrics_match:
                lyrics_html = lyrics_match.group(1)
                # Limpiar HTML y extraer texto
                lyrics = self._clean_html(lyrics_html)
                return lyrics.strip()
                
        except Exception:
            pass
            
        return None
    
    def _clean_html(self, html_content: str) -> str:
        """Limpia contenido HTML y extrae solo el texto"""
        # Remover tags HTML
        text = re.sub(r'<[^>]+>', '', html_content)
        # Limpiar espacios y saltos de línea excesivos
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def _validate_lyrics(self, lyrics: str) -> bool:
        """Valida que el contenido parezca ser letras reales"""
        if not lyrics or len(lyrics.strip()) < 50:
            return False
            
        # Verificar que no sea solo metadata
        words = lyrics.split()
        if len(words) < 10:
            return False
            
        # Verificar que no contenga demasiados caracteres especiales
        special_char_ratio = len(re.findall(r'[^\w\s\n\r\'".,!?()-]', lyrics)) / len(lyrics)
        if special_char_ratio > 0.3:
            return False
            
        return True
    
    def _format_lyrics(self, lyrics: str) -> str:
        """Formatea las letras para almacenamiento"""
        # Limpiar y formatear
        formatted = lyrics.strip()
        # Normalizar saltos de línea
        formatted = re.sub(r'\r\n|\r', '\n', formatted)
        # Remover líneas vacías excesivas
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)
        # Limitar longitud
        if len(formatted) > 10000:  # Máximo 10k caracteres
            formatted = formatted[:10000] + "..."
            
        return formatted
    
    async def _rate_limit(self, source: str):
        """Implementa rate limiting para las diferentes fuentes"""
        if source in self.rate_limits:
            last_time = self.last_request_time.get(source, 0)
            min_interval = self.rate_limits[source]
            elapsed = time.time() - last_time
            
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
                
            self.last_request_time[source] = time.time()


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
                youtube_id=song_model.source_id if song_model.source_type == 'youtube' else None
            )
            
            if lyrics:
                song_model.lyrics = lyrics
                await song_model.asave(update_fields=['lyrics'])
                self.logger.info(f"Letras actualizadas para: {song_model.title}")
                return True
            else:
                self.logger.debug(f"No se encontraron letras para: {song_model.title}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error actualizando letras para {song_model.title}: {str(e)}")
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
            'total_processed': total,
            'updated': updated,
            'errors': errors,
            'skipped': total - updated - errors
        }
        
        self.logger.info(f"Actualización masiva completada: {stats}")
        return stats
