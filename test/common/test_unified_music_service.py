"""
Tests para el servicio unificado de música
"""

<<<<<<< HEAD
from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.common.adapters.media.unified_music_service import UnifiedMusicService
from src.common.factories.unified_music_service_factory import (
    UnifiedMusicServiceFactory,
    get_music_service,
)
from src.common.types.media_types import (
    AudioTrackData,
    MusicServiceConfig,
    YouTubeVideoInfo,
=======
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.common.adapters.media.unified_music_service import UnifiedMusicService
from src.common.factories.unified_music_service_factory import (
    get_music_service,
    UnifiedMusicServiceFactory,
)
from src.common.types.media_types import (
    YouTubeVideoInfo,
    AudioTrackData,
    MusicServiceConfig,
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
)


class TestUnifiedMusicService:
    """Tests para el servicio unificado de música"""

    def setup_method(self):
        """Setup para cada test"""
        # Crear mocks de servicios auxiliares
        self.mock_youtube_service = AsyncMock()
        self.mock_audio_service = AsyncMock()

        # Configuraciones de prueba
        self.music_config = MusicServiceConfig(
            enable_audio_download=True, max_concurrent_operations=2
        )

        # Crear servicio unificado
        self.service = UnifiedMusicService(
            config=self.music_config,
            youtube_service=self.mock_youtube_service,
            audio_service=self.mock_audio_service,
        )

    @pytest.mark.asyncio
    async def test_search_and_process_music_success(self):
        """Test búsqueda exitosa de música"""
        # Mock data
        mock_video = YouTubeVideoInfo(
            video_id="test123",
            title="Test Song - Test Artist",
            channel_title="Test Channel",
            channel_id="channel123",
            thumbnail_url="https://example.com/thumb.jpg",
            description="Test description",
            duration_seconds=180,
            published_at=datetime.now(),
            view_count=1000,
            like_count=100,
            tags=["music"],
            category_id="10",
            genre="Pop",
            url="https://youtube.com/watch?v=test123",
        )

        # Configure mocks
        self.mock_youtube_service.search_videos = AsyncMock(return_value=[mock_video])

        # Execute
        result = await self.service.search_and_process_music(
            "test query", max_results=1
        )

        # Verify
        assert len(result) == 1
        assert result[0].video_id == "test123"
        assert result[0].title == mock_video.title
        assert (
            "Test Artist" in result[0].artist_name
            or result[0].artist_name == "Test Channel"
        )

    @pytest.mark.asyncio
    async def test_get_random_music_tracks_success(self):
        """Test obtención exitosa de música aleatoria"""
        # Mock data
        mock_video = YouTubeVideoInfo(
            video_id="random123",
            title="Random Song",
            channel_title="Random Artist",
            channel_id="random_channel",
            thumbnail_url="https://example.com/thumb.jpg",
            description="Random description",
            duration_seconds=200,
            published_at=datetime.now(),
            view_count=5000,
            like_count=250,
            tags=["random", "music"],
            category_id="10",
            genre="Rock",
            url="https://youtube.com/watch?v=random123",
        )

        # Configure mocks
        self.mock_youtube_service.get_random_videos = AsyncMock(
            return_value=[mock_video]
        )

        # Execute
        result = await self.service.get_random_music_tracks(max_results=1)

        # Verify
        assert len(result) == 1
        assert result[0].video_id == "random123"
        assert result[0].genre == "Rock"

    @pytest.mark.asyncio
    async def test_get_music_with_full_metadata(self):
        """Test obtención de música con metadatos completos"""
        # Mock video with extracted metadata
        mock_video = YouTubeVideoInfo(
            video_id="meta123",
            title="Song Title",
            channel_title="Artist Name",
            channel_id="artist_channel",
            thumbnail_url="https://example.com/thumb.jpg",
            description="Song from Album Name",
            duration_seconds=240,
            published_at=datetime.now(),
            view_count=10000,
            like_count=500,
            tags=["pop", "album"],
            category_id="10",
            genre="Pop",
            url="https://youtube.com/watch?v=meta123",
        )

        # Configure mocks
        self.mock_youtube_service.search_videos = AsyncMock(return_value=[mock_video])

        # Execute
        result = await self.service.get_music_with_full_metadata(
            query="test query", create_missing_entities=False
        )

        # Verify
        assert "query" in result
        assert "audio_tracks" in result
        assert "videos" in result
        assert "artists" in result
        assert "albums" in result
        assert "statistics" in result
        assert len(result["videos"]) == 1
        assert len(result["audio_tracks"]) == 1

    @pytest.mark.asyncio
    async def test_download_audio_from_video(self):
        """Test descarga de audio de video específico"""
        # Mock audio data
        mock_audio_data = b"fake_audio_data"
        self.mock_audio_service.download_audio = AsyncMock(return_value=mock_audio_data)

        # Execute
        result = await self.service.download_audio_from_video("test_video_id")

        # Verify
        assert result == mock_audio_data
        self.mock_audio_service.download_audio.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_video_to_audio_track(self):
        """Test conversión de video a audio track"""
        # Mock video
        mock_video = YouTubeVideoInfo(
            video_id="process123",
            title="Process Test",
            channel_title="Process Artist",
            channel_id="process_channel",
            thumbnail_url="https://example.com/thumb.jpg",
            description="Process description",
            duration_seconds=300,
            published_at=datetime.now(),
            view_count=2000,
            like_count=100,
            tags=["test"],
            category_id="10",
            genre="Electronic",
            url="https://youtube.com/watch?v=process123",
        )

        # Execute
        result = await self.service.process_video_to_audio_track(mock_video)

        # Verify
        assert result is not None
        assert isinstance(result, AudioTrackData)
        assert result.video_id == "process123"
        assert result.title == "Process Test"

    def test_configure_repositories(self):
        """Test configuración de repositorios"""
        mock_artist_repo = Mock()
        mock_album_repo = Mock()

        # Execute
        self.service.configure_repositories(mock_artist_repo, mock_album_repo)

        # Verify
        assert self.service.artist_repository == mock_artist_repo
        assert self.service.album_repository == mock_album_repo

    def test_get_service_metrics(self):
        """Test obtención de métricas del servicio"""
        # Modify some metrics
        self.service._metrics["searches_performed"] = 5
        self.service._metrics["videos_processed"] = 10

        # Execute
        metrics = self.service.get_service_metrics()

        # Verify
        assert "searches_performed" in metrics
        assert "videos_processed" in metrics
        assert metrics["searches_performed"] == 5
        assert metrics["videos_processed"] == 10

    @pytest.mark.asyncio
    async def test_cleanup(self):
        """Test limpieza de recursos"""
        # Execute (should not raise exception)
        await self.service.cleanup()

        # Verify that it completes without error
        assert True

    @pytest.mark.asyncio
    async def test_error_handling_in_search(self):
        """Test manejo de errores en búsqueda"""
        # Configure mock to raise exception
        self.mock_youtube_service.search_videos = AsyncMock(
            side_effect=Exception("API Error")
        )

        # Execute
        result = await self.service.search_and_process_music("test query")

        # Verify
        assert result == []
        assert self.service._metrics["errors"] > 0


class TestUnifiedMusicServiceFactory:
    """Tests para el factory del servicio unificado"""

    def test_create_default_service(self):
        """Test creación de servicio por defecto"""
        with patch("src.common.adapters.media.youtube_service.YouTubeAPIService"):
            with patch(
                "src.common.adapters.media.audio_download_service.AudioDownloadService"
            ):
                service = UnifiedMusicServiceFactory.create_default_service()

                assert isinstance(service, UnifiedMusicService)
                assert service.config.enable_audio_download is True
                assert service.config.max_concurrent_operations == 3

    def test_create_lightweight_service(self):
        """Test creación de servicio ligero"""
        with patch("src.common.adapters.media.youtube_service.YouTubeAPIService"):
            service = UnifiedMusicServiceFactory.create_lightweight_service()

            assert isinstance(service, UnifiedMusicService)
            assert service.config.enable_audio_download is False
            assert service.audio_service is None

    def test_create_production_service(self):
        """Test creación de servicio para producción"""
        with patch("src.common.adapters.media.youtube_service.YouTubeAPIService"):
            with patch(
                "src.common.adapters.media.audio_download_service.AudioDownloadService"
            ):
                service = UnifiedMusicServiceFactory.create_production_service()

                assert isinstance(service, UnifiedMusicService)
                assert (
                    service.config.max_concurrent_operations == 2
                )  # Conservador para producción

    def test_create_custom_service(self):
        """Test creación de servicio personalizado"""
        custom_config = MusicServiceConfig(
            enable_audio_download=False, max_concurrent_operations=1
        )

        with patch("src.common.adapters.media.youtube_service.YouTubeAPIService"):
            service = UnifiedMusicServiceFactory.create_custom_service(
                music_config=custom_config
            )

            assert isinstance(service, UnifiedMusicService)
            assert service.config.enable_audio_download is False
            assert service.config.max_concurrent_operations == 1

    def test_get_music_service_convenience_function(self):
        """Test función de conveniencia get_music_service"""
        with patch("src.common.adapters.media.youtube_service.YouTubeAPIService"):
            with patch(
                "src.common.adapters.media.audio_download_service.AudioDownloadService"
            ):
                # Test default
                service_default = get_music_service("default")
                assert isinstance(service_default, UnifiedMusicService)

                # Test lightweight
                service_light = get_music_service("lightweight")
                assert isinstance(service_light, UnifiedMusicService)
                assert service_light.config.enable_audio_download is False


class TestIntegrationScenarios:
    """Tests de escenarios de integración"""

    @pytest.mark.asyncio
    async def test_full_workflow_search_with_metadata(self):
        """Test del flujo completo de búsqueda con metadatos"""
        with patch(
            "src.common.adapters.media.youtube_service.YouTubeAPIService"
        ) as mock_youtube:
            with patch(
                "src.common.adapters.media.audio_download_service.AudioDownloadService"
            ):
                # Setup
                service = get_music_service("default")

                # Mock YouTube service methods
                mock_video = YouTubeVideoInfo(
                    video_id="integration123",
                    title="Integration Test - Test Artist",
                    channel_title="Test Channel",
                    channel_id="channel123",
                    thumbnail_url="https://example.com/thumb.jpg",
                    description="Integration test description",
                    duration_seconds=180,
                    published_at=datetime.now(),
                    view_count=1000,
                    like_count=100,
                    tags=["integration", "test"],
                    category_id="10",
                    genre="Test",
                    url="https://youtube.com/watch?v=integration123",
                )

                service.youtube_service.search_videos = AsyncMock(
                    return_value=[mock_video]
                )

                # Execute full workflow
                result = await service.get_music_with_full_metadata(
                    query="integration test", create_missing_entities=False
                )

                # Verify complete result structure
                assert "query" in result
                assert "audio_tracks" in result
                assert "videos" in result
                assert "artists" in result
                assert "albums" in result
                assert "statistics" in result
                assert "timestamp" in result

                # Verify data integrity
                assert len(result["videos"]) == 1
                assert len(result["audio_tracks"]) == 1
                assert result["videos"][0].video_id == "integration123"
                assert result["audio_tracks"][0].video_id == "integration123"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
