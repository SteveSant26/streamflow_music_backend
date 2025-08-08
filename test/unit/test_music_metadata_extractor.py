"""
🧪 TESTS UNITARIOS PARA MUSIC METADATA EXTRACTOR
==============================================
Tests completos para el extractor de metadatos musicales
"""
import pytest
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from common.utils.music_metadata_extractor import MusicMetadataExtractor
from common.types.media_types import YouTubeVideoInfo, ExtractedArtistInfo, ExtractedAlbumInfo


class TestMusicMetadataExtractor:
    """Tests unitarios para MusicMetadataExtractor"""

    @pytest.fixture
    def extractor(self):
        """Instancia del extractor de metadatos"""
        return MusicMetadataExtractor()

    @pytest.fixture
    def sample_video_info(self):
        """Información de video de prueba"""
        return YouTubeVideoInfo(
            id="test_video_123",
            title="Ed Sheeran - Shape of You (Official Video)",
            description="Official music video for Shape of You by Ed Sheeran from the album ÷ (Divide)",
            channel_title="Ed Sheeran",
            duration_seconds=234,
            view_count=5000000,
            published_at=datetime(2024, 1, 1),
            url="https://youtube.com/watch?v=test_video_123"
        )

    def test_init_patterns(self, extractor):
        """Test de inicialización de patrones"""
        assert len(extractor.artist_title_patterns) > 0
        assert len(extractor.album_patterns) > 0
        assert len(extractor.year_patterns) > 0
        assert len(extractor.album_exclusions) > 0
        assert len(extractor.collaboration_keywords) > 0

    def test_extract_artist_title_with_dash(self, extractor):
        """Test de extracción de artista-título con guión"""
        title = "Ed Sheeran - Shape of You"
        artist, song_title = extractor._extract_artist_title_from_text(title)
        
        assert artist == "Ed Sheeran"
        assert song_title == "Shape of You"

    def test_extract_artist_title_with_colon(self, extractor):
        """Test de extracción de artista-título con dos puntos"""
        title = "Taylor Swift: Shake It Off"
        artist, song_title = extractor._extract_artist_title_from_text(title)
        
        assert artist == "Taylor Swift"
        assert song_title == "Shake It Off"

    def test_extract_artist_title_with_quotes(self, extractor):
        """Test de extracción con comillas"""
        title = 'Adele "Hello" Official Video'
        artist, song_title = extractor._extract_artist_title_from_text(title)
        
        assert artist == "Adele"
        assert song_title == "Hello"

    def test_extract_artist_title_with_featuring(self, extractor):
        """Test de extracción con colaboraciones"""
        title = "Drake ft. Rihanna - Work"
        artist, song_title = extractor._extract_artist_title_from_text(title)
        
        assert artist == "Drake"
        assert song_title == "Work"

    def test_extract_artist_title_no_pattern_match(self, extractor):
        """Test sin patrón reconocible"""
        title = "Random video title without pattern"
        artist, song_title = extractor._extract_artist_title_from_text(title)
        
        assert artist is None
        assert song_title is None

    def test_extract_artists_from_title(self, extractor, sample_video_info):
        """Test de extracción de artistas desde título"""
        artists = extractor._extract_artists(sample_video_info)
        
        assert len(artists) > 0
        assert artists[0].name == "Ed Sheeran"
        assert artists[0].confidence_score > 0.5

    def test_extract_artists_from_channel(self, extractor):
        """Test de extracción de artistas desde canal"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Shape of You",
            description="",
            channel_title="Ed Sheeran Official",
            duration_seconds=234,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        artists = extractor._extract_artists(video_info)
        
        assert len(artists) > 0
        assert "Ed Sheeran" in artists[0].name

    def test_extract_artists_from_description(self, extractor):
        """Test de extracción de artistas desde descripción"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Amazing Song",
            description="Artist: Taylor Swift\nAlbum: 1989",
            channel_title="Music Channel",
            duration_seconds=200,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        artists = extractor._extract_artists(video_info)
        
        assert len(artists) > 0
        assert any("Taylor Swift" in artist.name for artist in artists)

    def test_extract_albums_from_description(self, extractor, sample_video_info):
        """Test de extracción de álbumes desde descripción"""
        albums = extractor._extract_albums(sample_video_info, [])
        
        assert len(albums) > 0
        # Debería encontrar "Divide" en la descripción
        assert any("Divide" in album.title for album in albums)

    def test_extract_albums_with_quotes(self, extractor):
        """Test de extracción de álbumes con comillas"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Song Title",
            description='From the album "1989" by Taylor Swift',
            channel_title="Music Channel",
            duration_seconds=200,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        albums = extractor._extract_albums(video_info, [])
        
        assert len(albums) > 0
        assert albums[0].title == "1989"

    def test_extract_albums_with_brackets(self, extractor):
        """Test de extracción de álbumes con corchetes"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Song Title [Red Album]",
            description="Great song",
            channel_title="Music Channel",
            duration_seconds=200,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        albums = extractor._extract_albums(video_info, [])
        
        assert len(albums) > 0
        assert albums[0].title == "Red Album"

    def test_album_exclusions(self, extractor):
        """Test de exclusiones de álbumes"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Song Title [Official Video]",
            description="",
            channel_title="Music Channel",
            duration_seconds=200,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        albums = extractor._extract_albums(video_info, [])
        
        # No debería encontrar "Official Video" como álbum
        assert not any("Official Video" in album.title for album in albums)

    def test_extract_year_from_description(self, extractor):
        """Test de extracción de año"""
        text = "Released in 2023, this amazing song"
        years = extractor._extract_years_from_text(text)
        
        assert 2023 in years

    def test_extract_multiple_years(self, extractor):
        """Test de extracción de múltiples años"""
        text = "Originally from 1995, remastered in 2020"
        years = extractor._extract_years_from_text(text)
        
        assert 1995 in years
        assert 2020 in years

    def test_extract_year_invalid_range(self, extractor):
        """Test de años fuera del rango válido"""
        text = "Released in 1800 and 2050"
        years = extractor._extract_years_from_text(text)
        
        # No debería encontrar años fuera del rango 1900-2029
        assert 1800 not in years
        assert 2050 not in years

    def test_detect_collaboration_ft(self, extractor):
        """Test de detección de colaboración con 'ft'"""
        title = "Artist ft. Guest Artist - Song Title"
        has_collab = extractor._has_collaboration_indicators(title)
        
        assert has_collab is True

    def test_detect_collaboration_featuring(self, extractor):
        """Test de detección de colaboración con 'featuring'"""
        title = "Artist featuring Guest - Song Title"
        has_collab = extractor._has_collaboration_indicators(title)
        
        assert has_collab is True

    def test_detect_collaboration_with_ampersand(self, extractor):
        """Test de detección de colaboración con '&'"""
        title = "Artist & Guest - Song Title"
        has_collab = extractor._has_collaboration_indicators(title)
        
        assert has_collab is True

    def test_no_collaboration_detected(self, extractor):
        """Test sin colaboración detectada"""
        title = "Simple Artist - Song Title"
        has_collab = extractor._has_collaboration_indicators(title)
        
        assert has_collab is False

    def test_clean_artist_name(self, extractor):
        """Test de limpieza de nombre de artista"""
        dirty_name = "Artist Name (Official)"
        clean_name = extractor._clean_artist_name(dirty_name)
        
        assert "(Official)" not in clean_name
        assert clean_name.strip() == "Artist Name"

    def test_clean_album_title(self, extractor):
        """Test de limpieza de título de álbum"""
        dirty_title = "Album Title [Deluxe Edition]"
        clean_title = extractor._clean_album_title(dirty_title)
        
        # Dependiendo de la implementación, puede o no limpiar esto
        assert len(clean_title) > 0

    def test_calculate_confidence_high(self, extractor):
        """Test de cálculo de confianza alta"""
        factors = {
            'title_match': True,
            'channel_match': True,
            'description_match': True,
            'official_indicator': True
        }
        
        confidence = extractor._calculate_confidence(factors)
        
        assert confidence > 0.8

    def test_calculate_confidence_low(self, extractor):
        """Test de cálculo de confianza baja"""
        factors = {
            'title_match': False,
            'channel_match': False,
            'description_match': False,
            'official_indicator': False
        }
        
        confidence = extractor._calculate_confidence(factors)
        
        assert confidence < 0.5

    def test_extract_music_metadata_complete(self, extractor, sample_video_info):
        """Test de extracción completa de metadatos"""
        result = extractor.extract_music_metadata(sample_video_info)
        
        assert result.extracted_artists is not None
        assert result.extracted_albums is not None
        assert len(result.extracted_artists) > 0

    def test_extract_music_metadata_minimal_info(self, extractor):
        """Test con información mínima"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Unknown Song",
            description="",
            channel_title="Random Channel",
            duration_seconds=200,
            view_count=100,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        result = extractor.extract_music_metadata(video_info)
        
        # Debería manejar información mínima sin errores
        assert result.extracted_artists is not None
        assert result.extracted_albums is not None

    def test_extract_with_special_characters(self, extractor):
        """Test con caracteres especiales"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Artíst Namé - Sóng Títle (Óficial Videó)",
            description="Spëcial charactërs in descriptions",
            channel_title="Artíst Channél",
            duration_seconds=200,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        result = extractor.extract_music_metadata(video_info)
        
        # Debería manejar caracteres especiales correctamente
        assert result.extracted_artists is not None
        assert len(result.extracted_artists) > 0

    def test_extract_with_very_long_title(self, extractor):
        """Test con título muy largo"""
        long_title = "Very Long Artist Name With Many Words " * 10 + "- Song Title"
        
        video_info = YouTubeVideoInfo(
            id="test",
            title=long_title,
            description="",
            channel_title="Channel",
            duration_seconds=200,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        result = extractor.extract_music_metadata(video_info)
        
        # Debería manejar títulos largos sin problemas
        assert result.extracted_artists is not None

    def test_extract_with_empty_fields(self, extractor):
        """Test con campos vacíos"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="",
            description="",
            channel_title="",
            duration_seconds=0,
            view_count=0,
            published_at=datetime.now(),
            url=""
        )
        
        result = extractor.extract_music_metadata(video_info)
        
        # Debería manejar campos vacíos sin errores
        assert result.extracted_artists is not None
        assert result.extracted_albums is not None

    def test_logging_integration(self, extractor):
        """Test de integración con logging"""
        assert hasattr(extractor, 'logger')
        assert extractor.logger is not None

    def test_pattern_case_insensitive(self, extractor):
        """Test de patrones insensibles a mayúsculas"""
        title = "ARTIST NAME - SONG TITLE"
        artist, song_title = extractor._extract_artist_title_from_text(title)
        
        assert artist is not None
        assert song_title is not None

    def test_extract_artists_with_numbers(self, extractor):
        """Test de extracción con números en nombres"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Maroon 5 - Sugar",
            description="",
            channel_title="Maroon5VEVO",
            duration_seconds=200,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        artists = extractor._extract_artists(video_info)
        
        assert len(artists) > 0
        assert "Maroon 5" in artists[0].name or "Maroon5" in artists[0].name

    def test_extract_with_remix_indicator(self, extractor):
        """Test con indicador de remix"""
        video_info = YouTubeVideoInfo(
            id="test",
            title="Artist - Song (Remix)",
            description="Remix version",
            channel_title="DJ Channel",
            duration_seconds=200,
            view_count=1000,
            published_at=datetime.now(),
            url="https://youtube.com/test"
        )
        
        result = extractor.extract_music_metadata(video_info)
        
        # Debería extraer información básica incluso con remix
        assert result.extracted_artists is not None
