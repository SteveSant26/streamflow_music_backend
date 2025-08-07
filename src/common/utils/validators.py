import re
from typing import Optional
from urllib.parse import urlparse

from ..mixins.logging_mixin import LoggingMixin


class URLValidator(LoggingMixin):
    """Validador de URLs para diferentes plataformas"""

    YOUTUBE_PATTERNS = [
        r"^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+",
        r"^https?://(?:www\.)?youtu\.be/[\w-]+",
        r"^https?://(?:www\.)?youtube\.com/embed/[\w-]+",
        r"^https?://(?:m\.)?youtube\.com/watch\?v=[\w-]+",
    ]

    def __init__(self):
        super().__init__()

    def validate_youtube_url(self, url: str) -> bool:
        """Valida si una URL pertenece a YouTube"""
        if not url or not isinstance(url, str):
            return False

        try:
            # Validar formato básico de URL
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            # Verificar patrones específicos de YouTube
            for pattern in self.YOUTUBE_PATTERNS:
                if re.match(pattern, url):
                    return True

            self.logger.debug(f"URL no coincide con patrones de YouTube: {url}")
            return False

        except Exception as e:
            self.logger.error(f"Error validando URL {url}: {str(e)}")
            return False

    def extract_video_id(self, url: str) -> Optional[str]:
        """Extrae el ID del video de una URL de YouTube"""
        if not self.validate_youtube_url(url):
            return None

        try:
            # Patrones para extraer video ID
            patterns = [
                r"(?:v=|/)([0-9A-Za-z_-]{11}).*",
                r"(?:embed/)([0-9A-Za-z_-]{11})",
                r"(?:youtu\.be/)([0-9A-Za-z_-]{11})",
            ]

            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)

            return None

        except Exception as e:
            self.logger.error(f"Error extrayendo video ID de {url}: {str(e)}")
            return None


class MediaDataValidator(LoggingMixin):
    """Validador para datos de medios"""

    VALID_AUDIO_FORMATS = [".mp3", ".m4a", ".webm", ".ogg", ".wav", ".flac"]
    VALID_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".webp", ".gif"]

    def __init__(self):
        super().__init__()

    def validate_audio_format(self, filename: str) -> bool:
        """Valida si el formato de archivo es de audio válido"""
        if not filename:
            return False

        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in self.VALID_AUDIO_FORMATS)

    def validate_image_format(self, filename: str) -> bool:
        """Valida si el formato de archivo es de imagen válido"""
        if not filename:
            return False

        filename_lower = filename.lower()
        return any(filename_lower.endswith(ext) for ext in self.VALID_IMAGE_FORMATS)

    def validate_duration(self, duration_seconds: int) -> bool:
        """Valida si la duración está en un rango razonable"""
        return 0 < duration_seconds <= 3600 * 2  # Máximo 2 horas

    def validate_filesize(
        self, size_bytes: int, max_size: int = 100 * 1024 * 1024
    ) -> bool:
        """Valida si el tamaño del archivo está dentro del límite"""
        return 0 < size_bytes <= max_size

    def sanitize_filename(self, filename: str) -> str:
        """Sanitiza un nombre de archivo removiendo caracteres no válidos"""
        if not filename:
            return "unknown"

        # Remover caracteres no válidos para nombres de archivo
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)

        # Remover espacios múltiples y al inicio/final
        sanitized = re.sub(r"\s+", " ", sanitized).strip()

        # Limitar longitud
        if len(sanitized) > 100:
            sanitized = sanitized[:100]

        return sanitized or "unknown"


class TextCleaner(LoggingMixin):
    """Limpiador de texto para títulos y metadatos"""

    COMMON_PATTERNS_TO_REMOVE = [
        r"\(Official[^\)]*\)",
        r"\[Official[^\]]*\]",
        r"Official Video",
        r"Official Audio",
        r"Music Video",
        r"Lyric Video",
        r"Lyrics Video",
        r"\bHD\b",
        r"\(HD\)",
        r"\[HD\]",
        r"\b4K\b",
        r"\(4K\)",
        r"\[4K\]",
        r"VEVO$",
        r"Records$",
        r"Music$",
    ]

    def __init__(self):
        super().__init__()

    def clean_title(self, title: str) -> str:
        """Limpia el título de una canción o video"""
        if not title:
            return "Unknown Title"

        cleaned = title

        # Aplicar patrones de limpieza
        for pattern in self.COMMON_PATTERNS_TO_REMOVE:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)

        # Extraer solo la parte del título si hay separador
        if " - " in cleaned:
            parts = cleaned.split(" - ")
            if len(parts) >= 2:
                cleaned = parts[1]

        # Limpiar espacios múltiples y espacios al inicio/final
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned or "Unknown Title"

    def extract_artist_from_title(self, title: str) -> Optional[str]:
        """Extrae el nombre del artista del título"""
        if not title:
            return None

        # Buscar patrón "Artista - Título"
        dash_pattern = r"^([^-]+)\s*-\s*(.+)$"
        match = re.match(dash_pattern, title)

        if match:
            artist_part = match.group(1).strip()
            # Limpiar patrones comunes
            artist_part = re.sub(r"\s*\(.*?\)\s*", "", artist_part)
            artist_part = re.sub(r"\s*\[.*?\]\s*", "", artist_part)
            return artist_part.strip() if artist_part.strip() else None

        return None

    def clean_channel_name(self, channel_name: str) -> str:
        """Limpia el nombre del canal para usar como artista"""
        if not channel_name:
            return "Unknown Artist"

        cleaned = channel_name

        # Limpiar sufijos comunes de canales
        suffixes_to_remove = ["VEVO", "Official", "Records", "Music", "Channel"]
        for suffix in suffixes_to_remove:
            cleaned = re.sub(f"{suffix}$", "", cleaned, flags=re.IGNORECASE)

        cleaned = cleaned.strip()
        return cleaned or "Unknown Artist"
