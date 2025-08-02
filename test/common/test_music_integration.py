"""
Tests para el servicio de integración musical mejorado
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.common.adapters.media.youtube_service import YouTubeAPIService
# from src.common.adapters.media.music_service_builder import MusicIntegrationService
from src.common.utils.music_metadata_extractor import MusicMetadataExtractor
from src.common.types.media_types import (
    YouTubeVideoInfo, 
    ExtractedArtistInfo, 
    ExtractedAlbumInfo,
    YouTubeServiceConfig
)
from src.apps.artists.domain.entities import ArtistEntity
from src.apps.albums.domain.entities import AlbumEntity


class TestMusicMetadataExtractor:
    """Tests para el extractor de metadatos musicales"""
    
    def setup_method(self):
        self.extractor = MusicMetadataExtractor()
    
    def test_extract_artist_from_title_basic(self):
        """Test extracción básica de artista desde título"""
        video_info = YouTubeVideoInfo(
            video_id="test123",
            title="Taylor Swift - Shake It Off",
            channel_title="TaylorSwiftVEVO",
            channel_id="UCqECaJ8Gagnn7YCbPEzWH6g",
            thumbnail_url="https://example.com/thumb.jpg",
            description="Official music video",
            duration_seconds=242,
            published_at=datetime.now(),
            view_count=1000000,
            like_count=50000,
            tags=["pop", "music"],
            category_id="10",
            genre="Pop",
            url="https://youtube.com/watch?v=test123"
        )
        
        result = self.extractor.extract_music_metadata(video_info)
        
        assert len(result.extracted_artists) > 0
        main_artist = result.extracted_artists[0]
        assert "taylor swift" in main_artist.name.lower()
        assert main_artist.confidence_score > 0.5
    
    def test_extract_album_from_description(self):
        """Test extracción de álbum desde descripción"""
        video_info = YouTubeVideoInfo(
            video_id="test123",
            title="Shake It Off",
            channel_title="TaylorSwiftVEVO",
            channel_id="UCqECaJ8Gagnn7YCbPEzWH6g",
            thumbnail_url="https://example.com/thumb.jpg",
            description="From the album '1989' by Taylor Swift",
            duration_seconds=242,
            published_at=datetime.now(),
            view_count=1000000,
            like_count=50000,
            tags=["pop", "music"],
            category_id="10",
            genre="Pop",
            url="https://youtube.com/watch?v=test123"
        )
        
        # Mock para que extraiga artistas primero
        with patch.object(self.extractor, '_extract_artists') as mock_extract_artists:
            mock_extract_artists.return_value = [
                ExtractedArtistInfo(
                    name="Taylor Swift",
                    extracted_from="channel",
                    confidence_score=0.8
                )
            ]
            
            result = self.extractor.extract_music_metadata(video_info)
            
            assert len(result.extracted_albums) > 0
            main_album = result.extracted_albums[0]
            assert "1989" in main_album.title
            assert main_album.artist_name == "Taylor Swift"


class TestYouTubeServiceEnhancements:
    """Tests para las mejoras del servicio de YouTube"""
    
    def setup_method(self):
        self.config = YouTubeServiceConfig(enable_quota_tracking=True)
        with patch('src.common.adapters.media.youtube_service.build'):
            self.service = YouTubeAPIService(config=self.config)
    
    def test_quota_tracking(self):
        """Test seguimiento de cuota"""
        # Verificar estado inicial
        quota_info = self.service.get_quota_usage()
        assert quota_info['quota_used'] == 0
        assert quota_info['quota_remaining'] == self.config.quota_limit_per_day
        
        # Simular uso de cuota
        self.service.quota_used_today = 100
        quota_info = self.service.get_quota_usage()
        assert quota_info['quota_used'] == 100
        assert quota_info['quota_remaining'] == self.config.quota_limit_per_day - 100
    
    def test_check_quota_limit(self):
        """Test verificación de límite de cuota"""
        # Dentro del límite
        assert self.service._check_quota_limit(100) == True
        
        # Cerca del límite
        self.service.quota_used_today = self.config.quota_limit_per_day - 50
        assert self.service._check_quota_limit(40) == True
        assert self.service._check_quota_limit(60) == False
    
    # NOTE: This test was disabled because get_extracted_artists_summary method
    # was removed during simplification - it was only used in tests
    # def test_get_extracted_artists_summary(self):
    #     """Test resumen de artistas extraídos"""
    #     videos = [
    #         YouTubeVideoInfo(
    #             video_id="test1",
    #             title="Test Song",
    #             channel_title="TestChannel",
    #             channel_id="test123",
    #             thumbnail_url="",
    #             description="",
    #             duration_seconds=180,
    #             published_at=datetime.now(),
    #             view_count=1000,
    #             like_count=100,
    #             tags=[],
    #             category_id="10",
    #             genre="Pop",
    #             url="https://youtube.com/watch?v=test1",
    #             extracted_artists=[
    #                 ExtractedArtistInfo(
    #                     name="Test Artist",
    #                     extracted_from="title",
    #                     confidence_score=0.8
    #                 )
    #             ]
    #         )
    #     ]
    #     
    #     summary = self.service.get_extracted_artists_summary(videos)
    #     
    #     assert summary['total_videos'] == 1
    #     assert summary['unique_artists'] == 1
    #     assert 'Test Artist' in summary['artists']
    #     assert summary['artists']['Test Artist']['average_confidence'] == 0.8


class TestMusicIntegrationService:
    """Tests para el servicio de integración musical"""
    
    def setup_method(self):
        self.mock_youtube_service = Mock(spec=YouTubeAPIService)
        self.mock_artist_repo = AsyncMock()
        self.mock_album_repo = AsyncMock()
        
        self.integration_service = MusicIntegrationService(
            youtube_service=self.mock_youtube_service,
            artist_repository=self.mock_artist_repo,
            album_repository=self.mock_album_repo
        )
    
    @pytest.mark.asyncio
    async def test_get_random_music_with_metadata_success(self):
        """Test obtención exitosa de música random con metadatos"""
        # Mock del servicio de YouTube
        mock_videos = [
            YouTubeVideoInfo(
                video_id="test1",
                title="Test Song - Test Artist",
                channel_title="TestChannel",
                channel_id="test123",
                thumbnail_url="",
                description="",
                duration_seconds=180,
                published_at=datetime.now(),
                view_count=1000,
                like_count=100,
                tags=[],
                category_id="10",
                genre="Pop",
                url="https://youtube.com/watch?v=test1",
                extracted_artists=[
                    ExtractedArtistInfo(
                        name="Test Artist",
                        extracted_from="title",
                        confidence_score=0.8
                    )
                ]
            )
        ]
        
        self.mock_youtube_service.get_random_videos = AsyncMock(return_value=mock_videos)
        # Note: get_extracted_artists_summary and get_extracted_albums_summary were removed
        # The metadata is now extracted automatically in the get_random_videos method
        
        # Mock del repositorio de artistas
        self.mock_artist_repo.get_by_name = AsyncMock(return_value=None)
        self.mock_artist_repo.search_by_similar_name = AsyncMock(return_value=[])
        
        # Ejecutar
        result = await self.integration_service.get_random_music_with_metadata()
        
        # Verificar
        assert len(result['videos']) == 1
        assert result['statistics']['videos']['total'] == 1
        assert len(result['artists']['not_found_in_db']) == 1
    
    @pytest.mark.asyncio
    async def test_process_extracted_artists_found_in_db(self):
        """Test procesamiento de artistas encontrados en BD"""
        # Datos de prueba
        videos = [
            YouTubeVideoInfo(
                video_id="test1",
                title="Test Song",
                channel_title="TestChannel",
                channel_id="test123",
                thumbnail_url="",
                description="",
                duration_seconds=180,
                published_at=datetime.now(),
                view_count=1000,
                like_count=100,
                tags=[],
                category_id="10",
                genre="Pop",
                url="https://youtube.com/watch?v=test1",
                extracted_artists=[
                    ExtractedArtistInfo(
                        name="Known Artist",
                        extracted_from="title",
                        confidence_score=0.9
                    )
                ]
            )
        ]
        
        # Mock artista existente en BD
        existing_artist = ArtistEntity(
            id="artist123",
            name="Known Artist",
            biography="Test artist",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.mock_artist_repo.get_by_name = AsyncMock(return_value=existing_artist)
        
        # Ejecutar
        result = await self.integration_service._process_extracted_artists(videos, False)
        
        # Verificar
        assert len(result['found_in_db']) == 1
        assert result['found_in_db'][0]['entity'].name == "Known Artist"
        assert len(result['not_found_in_db']) == 0
    
    @pytest.mark.asyncio
    async def test_create_artist_from_extraction(self):
        """Test creación de artista desde extracción"""
        artist_info = ExtractedArtistInfo(
            name="New Artist",
            extracted_from="title", 
            confidence_score=0.7
        )
        
        # Mock creación exitosa
        created_artist = ArtistEntity(
            id="new_artist_123",
            name="New Artist",
            biography="Artista descubierto desde YouTube (confianza: 0.70)",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.mock_artist_repo.create = AsyncMock(return_value=created_artist)
        
        # Ejecutar
        result = await self.integration_service._create_artist_from_extraction(artist_info)
        
        # Verificar
        assert result is not None
        assert result.name == "New Artist"
        self.mock_artist_repo.create.assert_called_once()
    
    def test_calculate_artist_match_confidence(self):
        """Test cálculo de confianza de match de artistas"""
        db_artist = ArtistEntity(
            id="artist123",
            name="Test Artist",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        extracted_artist = ExtractedArtistInfo(
            name="Test Artist",
            extracted_from="title",
            confidence_score=0.8
        )
        
        # Match exacto
        confidence = self.integration_service._calculate_artist_match_confidence(db_artist, extracted_artist)
        assert confidence == 1.0
        
        # Match parcial
        extracted_artist.name = "Different Artist"
        confidence = self.integration_service._calculate_artist_match_confidence(db_artist, extracted_artist)
        assert confidence == 0.8 * 0.8  # confidence_score * 0.8
    
    def test_generate_integration_stats(self):
        """Test generación de estadísticas de integración"""
        videos = [
            YouTubeVideoInfo(
                video_id="test1",
                title="Test Song",
                channel_title="TestChannel",
                channel_id="test123",
                thumbnail_url="",
                description="",
                duration_seconds=180,
                published_at=datetime.now(),
                view_count=1000,
                like_count=100,
                tags=[],
                category_id="10",
                genre="Pop",
                url="https://youtube.com/watch?v=test1",
                extracted_artists=[ExtractedArtistInfo(name="Artist", extracted_from="title", confidence_score=0.8)],
                extracted_albums=[ExtractedAlbumInfo(title="Album", extracted_from="title", confidence_score=0.7)]
            )
        ]
        
        artists_info = {
            "found_in_db": [],
            "not_found_in_db": [ExtractedArtistInfo(name="Artist", extracted_from="title", confidence_score=0.8)],
            "created": [],
            "extraction_details": [ExtractedArtistInfo(name="Artist", extracted_from="title", confidence_score=0.8)]
        }
        
        albums_info = {
            "found_in_db": [],
            "not_found_in_db": [ExtractedAlbumInfo(title="Album", extracted_from="title", confidence_score=0.7)],
            "created": [],
            "extraction_details": [ExtractedAlbumInfo(title="Album", extracted_from="title", confidence_score=0.7)]
        }
        
        stats = self.integration_service._generate_integration_stats(videos, artists_info, albums_info)
        
        assert stats['videos']['total'] == 1
        assert stats['videos']['with_artists'] == 1
        assert stats['videos']['with_albums'] == 1
        assert stats['videos']['with_both'] == 1
        assert stats['artists']['total_extracted'] == 1
        assert stats['albums']['total_extracted'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
