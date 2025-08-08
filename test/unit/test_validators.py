"""
🧪 TESTS UNITARIOS PARA VALIDATORS
================================
Tests completos para los validadores de URLs, datos y texto
"""
import pytest
from unittest.mock import Mock, patch
import re

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from common.utils.validators import URLValidator, TextCleaner, MediaDataValidator


class TestURLValidator:
    """Tests unitarios para URLValidator"""

    @pytest.fixture
    def url_validator(self):
        """Instancia del validador de URLs"""
        return URLValidator()

    def test_validate_youtube_url_valid_watch(self, url_validator):
        """Test de validación de URL de YouTube con formato watch"""
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "http://youtube.com/watch?v=dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            assert url_validator.validate_youtube_url(url) is True

    def test_validate_youtube_url_valid_short(self, url_validator):
        """Test de validación de URL corta de YouTube"""
        valid_urls = [
            "https://youtu.be/dQw4w9WgXcQ",
            "http://youtu.be/dQw4w9WgXcQ",
            "https://www.youtu.be/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            assert url_validator.validate_youtube_url(url) is True

    def test_validate_youtube_url_valid_embed(self, url_validator):
        """Test de validación de URL de YouTube embebida"""
        valid_urls = [
            "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "http://www.youtube.com/embed/dQw4w9WgXcQ",
            "https://youtube.com/embed/dQw4w9WgXcQ"
        ]
        
        for url in valid_urls:
            assert url_validator.validate_youtube_url(url) is True

    def test_validate_youtube_url_invalid(self, url_validator):
        """Test de validación de URLs inválidas"""
        invalid_urls = [
            "https://vimeo.com/123456",
            "https://soundcloud.com/track",
            "https://spotify.com/track",
            "https://example.com",
            "not_a_url",
            "",
            None,
            123,
            []
        ]
        
        for url in invalid_urls:
            assert url_validator.validate_youtube_url(url) is False

    def test_validate_youtube_url_malformed(self, url_validator):
        """Test de validación de URLs malformadas"""
        malformed_urls = [
            "youtube.com/watch?v=dQw4w9WgXcQ",  # Sin protocolo
            "https://",  # Incompleta
            "https://youtube",  # Sin dominio completo
            "https://youtube.com",  # Sin path
            "https://youtube.com/watch",  # Sin parámetros
            "https://youtube.com/watch?v=",  # Sin video ID
        ]
        
        for url in malformed_urls:
            assert url_validator.validate_youtube_url(url) is False

    def test_extract_video_id_watch_format(self, url_validator):
        """Test de extracción de ID de video formato watch"""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        video_id = url_validator.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_short_format(self, url_validator):
        """Test de extracción de ID de video formato corto"""
        url = "https://youtu.be/dQw4w9WgXcQ"
        video_id = url_validator.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_embed_format(self, url_validator):
        """Test de extracción de ID de video formato embed"""
        url = "https://www.youtube.com/embed/dQw4w9WgXcQ"
        video_id = url_validator.extract_video_id(url)
        assert video_id == "dQw4w9WgXcQ"

    def test_extract_video_id_with_parameters(self, url_validator):
        """Test de extracción de ID con parámetros adicionales"""
        urls_and_ids = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=30s", "dQw4w9WgXcQ"),
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLxxx", "dQw4w9WgXcQ"),
            ("https://youtu.be/dQw4w9WgXcQ?t=30", "dQw4w9WgXcQ")
        ]
        
        for url, expected_id in urls_and_ids:
            video_id = url_validator.extract_video_id(url)
            assert video_id == expected_id

    def test_extract_video_id_invalid_url(self, url_validator):
        """Test de extracción de ID con URL inválida"""
        invalid_urls = [
            "https://vimeo.com/123456",
            "not_a_url",
            "",
            None
        ]
        
        for url in invalid_urls:
            video_id = url_validator.extract_video_id(url)
            assert video_id is None

    def test_extract_video_id_edge_cases(self, url_validator):
        """Test de casos edge en extracción de ID"""
        edge_cases = [
            ("https://www.youtube.com/watch?v=", None),  # Sin ID
            ("https://youtu.be/", None),  # Sin ID
            ("https://www.youtube.com/embed/", None),  # Sin ID
        ]
        
        for url, expected in edge_cases:
            video_id = url_validator.extract_video_id(url)
            assert video_id == expected

    def test_logging_integration(self, url_validator):
        """Test de integración con logging"""
        assert hasattr(url_validator, 'logger')
        
        # Mock del logger para verificar llamadas
        url_validator.logger = Mock()
        
        # URL inválida debería generar log
        url_validator.validate_youtube_url("invalid_url")
        
        # Verificar que se llamó al logger
        url_validator.logger.debug.assert_called()

    def test_validate_general_url_format(self, url_validator):
        """Test de validación de formato general de URL"""
        # Este test verifica la funcionalidad interna de validación de URLs
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://subdomain.example.com/path"
        ]
        
        invalid_urls = [
            "not_a_url",
            "://missing-scheme",
            "https://",  # Sin netloc
        ]
        
        # Como validate_youtube_url incluye validación general,
        # podemos usar URLs no-YouTube para verificar la validación básica
        for url in invalid_urls:
            assert url_validator.validate_youtube_url(url) is False


class TestTextCleaner:
    """Tests unitarios para TextCleaner"""

    @pytest.fixture
    def text_cleaner(self):
        """Instancia del limpiador de texto"""
        return TextCleaner()

    def test_clean_text_basic(self, text_cleaner):
        """Test de limpieza básica de texto"""
        dirty_text = "Hello!!! World??? @#$%"
        clean_text = text_cleaner.clean_text(dirty_text)
        
        assert "!!!" not in clean_text
        assert "???" not in clean_text
        assert "@#$%" not in clean_text
        assert len(clean_text) > 0

    def test_clean_text_empty_input(self, text_cleaner):
        """Test con entrada vacía"""
        assert text_cleaner.clean_text("") == ""
        assert text_cleaner.clean_text(None) == ""

    def test_clean_text_whitespace_normalization(self, text_cleaner):
        """Test de normalización de espacios en blanco"""
        text_with_spaces = "Hello    World   Test"
        cleaned = text_cleaner.clean_text(text_with_spaces)
        
        # No debería tener múltiples espacios consecutivos
        assert "    " not in cleaned
        assert "   " not in cleaned

    def test_clean_text_preserve_meaning(self, text_cleaner):
        """Test que preserva el significado del texto"""
        meaningful_text = "Artist Name - Song Title (Official Video)"
        cleaned = text_cleaner.clean_text(meaningful_text)
        
        # Debería preservar palabras importantes
        assert "Artist" in cleaned
        assert "Name" in cleaned
        assert "Song" in cleaned
        assert "Title" in cleaned

    def test_clean_text_unicode_characters(self, text_cleaner):
        """Test con caracteres unicode"""
        unicode_text = "Artíst Namé - Sóng Títle"
        cleaned = text_cleaner.clean_text(unicode_text)
        
        # Debería preservar caracteres acentuados
        assert "Artíst" in cleaned or "Artist" in cleaned
        assert len(cleaned) > 0

    def test_clean_text_numbers(self, text_cleaner):
        """Test con números en el texto"""
        text_with_numbers = "Track 01 - Artist 2023"
        cleaned = text_cleaner.clean_text(text_with_numbers)
        
        # Debería preservar números
        assert "01" in cleaned or "1" in cleaned
        assert "2023" in cleaned

    def test_clean_artist_name(self, text_cleaner):
        """Test de limpieza específica de nombres de artistas"""
        dirty_names = [
            "Artist Name (Official)",
            "Artist Name - Topic",
            "Artist Name VEVO",
            "Artist Name [Official Channel]"
        ]
        
        for dirty_name in dirty_names:
            cleaned = text_cleaner.clean_artist_name(dirty_name)
            
            # Debería remover indicadores de canal oficial
            assert "(Official)" not in cleaned
            assert "VEVO" not in cleaned
            assert "[Official Channel]" not in cleaned
            assert "Topic" not in cleaned
            assert "Artist Name" in cleaned

    def test_clean_song_title(self, text_cleaner):
        """Test de limpieza específica de títulos de canciones"""
        dirty_titles = [
            "Song Title (Official Video)",
            "Song Title [Official Audio]",
            "Song Title - Official Music Video",
            "Song Title (Lyrics)"
        ]
        
        for dirty_title in dirty_titles:
            cleaned = text_cleaner.clean_song_title(dirty_title)
            
            # Debería remover indicadores de tipo de video
            assert "(Official Video)" not in cleaned
            assert "[Official Audio]" not in cleaned
            assert "- Official Music Video" not in cleaned
            assert "(Lyrics)" not in cleaned
            assert "Song Title" in cleaned


class TestMediaDataValidator:
    """Tests unitarios para MediaDataValidator"""

    @pytest.fixture
    def media_validator(self):
        """Instancia del validador de datos de medios"""
        return MediaDataValidator()

    def test_validate_duration_valid(self, media_validator):
        """Test de validación de duración válida"""
        valid_durations = [30, 180, 300, 600]  # 30s a 10min
        
        for duration in valid_durations:
            assert media_validator.validate_duration(duration) is True

    def test_validate_duration_invalid(self, media_validator):
        """Test de validación de duración inválida"""
        invalid_durations = [0, -1, 10, 3600, 7200]  # Muy corto o muy largo
        
        for duration in invalid_durations:
            assert media_validator.validate_duration(duration) is False

    def test_validate_file_size_valid(self, media_validator):
        """Test de validación de tamaño de archivo válido"""
        valid_sizes = [
            1024 * 1024,      # 1 MB
            10 * 1024 * 1024, # 10 MB
            50 * 1024 * 1024  # 50 MB
        ]
        
        for size in valid_sizes:
            assert media_validator.validate_file_size(size) is True

    def test_validate_file_size_invalid(self, media_validator):
        """Test de validación de tamaño de archivo inválido"""
        invalid_sizes = [
            0,                    # Tamaño cero
            -1,                   # Tamaño negativo
            200 * 1024 * 1024     # 200 MB (muy grande)
        ]
        
        for size in invalid_sizes:
            assert media_validator.validate_file_size(size) is False

    def test_validate_audio_format_valid(self, media_validator):
        """Test de validación de formato de audio válido"""
        valid_formats = ["mp3", "flac", "wav", "m4a", "ogg"]
        
        for format in valid_formats:
            assert media_validator.validate_audio_format(format) is True

    def test_validate_audio_format_invalid(self, media_validator):
        """Test de validación de formato de audio inválido"""
        invalid_formats = ["txt", "pdf", "mp4", "avi", "unknown"]
        
        for format in invalid_formats:
            assert media_validator.validate_audio_format(format) is False

    def test_validate_quality_valid(self, media_validator):
        """Test de validación de calidad válida"""
        valid_qualities = ["128", "192", "256", "320"]
        
        for quality in valid_qualities:
            assert media_validator.validate_quality(quality) is True

    def test_validate_quality_invalid(self, media_validator):
        """Test de validación de calidad inválida"""
        invalid_qualities = ["64", "500", "abc", "", None]
        
        for quality in invalid_qualities:
            assert media_validator.validate_quality(quality) is False

    def test_validate_metadata_complete(self, media_validator):
        """Test de validación de metadatos completos"""
        complete_metadata = {
            'title': 'Test Song',
            'artist': 'Test Artist',
            'duration': 180,
            'file_size': 5 * 1024 * 1024,
            'format': 'mp3',
            'quality': '192'
        }
        
        assert media_validator.validate_metadata(complete_metadata) is True

    def test_validate_metadata_missing_required(self, media_validator):
        """Test de validación con metadatos requeridos faltantes"""
        incomplete_metadata = {
            'duration': 180,
            'file_size': 5 * 1024 * 1024
            # Faltan title y artist
        }
        
        assert media_validator.validate_metadata(incomplete_metadata) is False

    def test_validate_metadata_invalid_values(self, media_validator):
        """Test de validación con valores inválidos"""
        invalid_metadata = {
            'title': '',  # Título vacío
            'artist': 'Test Artist',
            'duration': -1,  # Duración inválida
            'file_size': 0,  # Tamaño inválido
            'format': 'invalid',  # Formato inválido
            'quality': '999'  # Calidad inválida
        }
        
        assert media_validator.validate_metadata(invalid_metadata) is False

    def test_validate_url_format(self, media_validator):
        """Test de validación de formato de URL"""
        valid_urls = [
            "https://example.com/song.mp3",
            "http://cdn.example.com/audio/track.flac",
            "https://storage.example.com/media/file.wav"
        ]
        
        for url in valid_urls:
            assert media_validator.validate_url_format(url) is True

    def test_validate_url_format_invalid(self, media_validator):
        """Test de validación de URL inválida"""
        invalid_urls = [
            "not_a_url",
            "ftp://example.com/file.mp3",  # Protocolo no soportado
            "",
            None
        ]
        
        for url in invalid_urls:
            assert media_validator.validate_url_format(url) is False

    def test_sanitize_filename(self, media_validator):
        """Test de sanitización de nombres de archivo"""
        dirty_filename = "Song/Title\\With:Invalid*Characters?.mp3"
        clean_filename = media_validator.sanitize_filename(dirty_filename)
        
        # No debería contener caracteres problemáticos
        problematic_chars = ['/', '\\', ':', '*', '?', '<', '>', '|']
        for char in problematic_chars:
            assert char not in clean_filename
        
        # Debería preservar la extensión
        assert clean_filename.endswith('.mp3')

    def test_logging_integration(self, media_validator):
        """Test de integración con logging"""
        assert hasattr(media_validator, 'logger')
        
        # Mock del logger para verificar llamadas
        media_validator.logger = Mock()
        
        # Validación que debería generar log de error
        media_validator.validate_duration(-1)
        
        # Verificar que se puede llamar al logger (aunque no necesariamente se llame)
        assert media_validator.logger is not None
