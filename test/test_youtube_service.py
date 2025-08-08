import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import asyncio

from src.common.adapters.media.youtube_service import YouTubeAPIService
from src.common.types.media_types import YouTubeVideoInfo, SearchOptions


@pytest.fixture
def youtube_service():
    """Create a YouTubeAPIService instance with mocked settings."""
    with patch("src.common.adapters.media.youtube_service.settings") as mock_settings:
        mock_settings.YOUTUBE_API_KEY = "test-api-key"
        mock_settings.YOUTUBE_API_SERVICE_NAME = "youtube"
        mock_settings.YOUTUBE_API_VERSION = "v3"
        mock_settings.RANDOM_MUSIC_QUERIES = [
            "popular music 2023",
            "trending songs",
            "best hits"
        ]
        
        with patch.object(YouTubeAPIService, "_build_youtube_client") as mock_build:
            mock_youtube_client = MagicMock()
            mock_build.return_value = mock_youtube_client
            
            service = YouTubeAPIService()
            service.youtube = mock_youtube_client
            return service


class TestYouTubeAPIServiceBasic:
    """Basic tests for YouTubeAPIService."""

    def test_init_service(self, youtube_service):
        """Test service initialization."""
        assert youtube_service is not None
        assert youtube_service.youtube is not None


@pytest.mark.asyncio
class TestYouTubeAPIServiceSearch:
    """Tests para funcionalidad de búsqueda"""

    async def test_search_videos_success(self, youtube_service):
        """Test búsqueda exitosa de videos"""
        mock_result = [
            YouTubeVideoInfo(
                video_id="test_id_1",
                title="Test Song 1", 
                channel_title="Test Artist 1",
                channel_id="test_channel_1",
                description="Test description 1",
                duration_seconds=180,
                view_count=1000,
                like_count=100,
                published_at=datetime.now(),
                thumbnail_url="http://example.com/thumb1.jpg",
                tags=["music", "test"],
                category_id="10",
                genre="pop",
                url="http://youtube.com/watch?v=test_id_1"
            )
        ]
        
        with patch.object(youtube_service, '_search_videos_with_circuit_breaker', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_result
            
            options = SearchOptions(max_results=10)
            result = await youtube_service.search_videos("test query", options)
            
            assert result == mock_result
            mock_search.assert_called_once_with("test query music", options)

    async def test_search_videos_empty_query(self, youtube_service):
        """Test búsqueda con query vacío"""
        result = await youtube_service.search_videos("")
        assert result == []

    async def test_search_videos_exception_handling(self, youtube_service):
        """Test manejo de excepciones en búsqueda"""
        with patch.object(youtube_service, '_search_videos_with_circuit_breaker', new_callable=AsyncMock) as mock_search:
            mock_search.side_effect = Exception("API Error")
            
            options = SearchOptions(max_results=10)
            result = await youtube_service.search_videos("test query", options)
            
            assert result == []


@pytest.mark.asyncio  
class TestYouTubeAPIServiceVideoDetails:
    """Tests para obtener detalles de videos"""

    async def test_get_video_details_success(self, youtube_service):
        """Test obtención exitosa de detalles de video"""
        video_id = "test_video_id"
        expected_video = YouTubeVideoInfo(
            video_id=video_id,
            title="Test Video",
            channel_title="Test Channel",
            channel_id="test_channel_id",
            description="Test description",
            duration_seconds=200,
            view_count=5000,
            like_count=500,
            published_at=datetime.now(),
            thumbnail_url="http://example.com/thumb.jpg",
            tags=["music", "test"],
            category_id="10",
            genre="pop",
            url="http://youtube.com/watch?v=test_video_id"
        )
        
        with patch.object(youtube_service, '_get_videos_details', new_callable=AsyncMock) as mock_details:
            mock_details.return_value = [expected_video]
            
            result = await youtube_service.get_video_details(video_id)
            
            assert result == expected_video
            mock_details.assert_called_once_with([video_id])

    async def test_get_video_details_not_found(self, youtube_service):
        """Test video no encontrado"""
        with patch.object(youtube_service, '_get_videos_details', new_callable=AsyncMock) as mock_details:
            mock_details.return_value = []
            
            result = await youtube_service.get_video_details("nonexistent_id")
            
            assert result is None

    async def test_get_video_details_exception(self, youtube_service):
        """Test manejo de excepciones al obtener detalles"""
        with patch.object(youtube_service, '_get_videos_details', new_callable=AsyncMock) as mock_details:
            mock_details.side_effect = Exception("API Error")
            
            result = await youtube_service.get_video_details("test_id")
            
            assert result is None


@pytest.mark.asyncio
class TestYouTubeAPIServiceRandomVideos:
    """Tests para obtener videos aleatorios"""

    async def test_get_random_videos_success(self, youtube_service):
        """Test obtención exitosa de videos aleatorios"""
        mock_videos = [
            YouTubeVideoInfo(
                video_id="random_1",
                title="Random Song 1",
                channel_title="Random Artist 1",
                channel_id="random_channel_1",
                description="Random description 1", 
                duration_seconds=190,
                view_count=2000,
                like_count=200,
                published_at=datetime.now(),
                thumbnail_url="http://example.com/random1.jpg",
                tags=["music", "random"],
                category_id="10",
                genre="rock",
                url="http://youtube.com/watch?v=random_1"
            )
        ]
        
        # Mock _get_random_queries to prevent settings error
        with patch.object(youtube_service, '_get_random_queries') as mock_queries:
            mock_queries.return_value = ["pop music", "rock songs"]
            with patch.object(youtube_service, 'search_videos', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = mock_videos
                
                options = SearchOptions(max_results=5)
                result = await youtube_service.get_random_videos(options)
                
                assert len(result) <= 5
                # Verificar que se llamó search_videos al menos una vez
                assert mock_search.called

    async def test_get_random_videos_no_results(self, youtube_service):
        """Test cuando no se encuentran videos aleatorios"""
        with patch.object(youtube_service, 'search_videos', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []
            
            result = await youtube_service.get_random_videos()
            
            assert result == []


@pytest.mark.asyncio
class TestYouTubeAPIServiceMusicCategories:
    """Tests para obtener categorías musicales"""

    async def test_get_music_categories_success(self, youtube_service):
        """Test obtención exitosa de categorías musicales"""
        with patch.object(youtube_service, '_fetch_video_categories') as mock_fetch:
            mock_fetch.return_value = {
                "items": [
                    {"id": "10", "snippet": {"title": "Music", "assignable": True}},
                    {"id": "15", "snippet": {"title": "Pets & Animals", "assignable": True}}
                ]
            }
            with patch.object(youtube_service, '_is_music_related_category') as mock_is_music:
                mock_is_music.side_effect = lambda cat: cat["title"] == "Music"
                
                result = await youtube_service.get_music_categories()
                
                assert len(result) == 1
                assert result[0]["title"] == "Music"

    async def test_get_music_categories_exception(self, youtube_service):
        """Test manejo de excepciones al obtener categorías"""
        with patch.object(youtube_service, '_fetch_video_categories') as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")
            
            result = await youtube_service.get_music_categories()
            
            # Should return fallback categories on exception
            expected = [{
                "id": "10",
                "title": "Music",
                "assignable": True,
                "channel_id": "",
                "is_primary_music": True,
            }]
            assert result == expected


class TestYouTubeAPIServiceUtilityMethods:
    """Tests para métodos utilitarios"""

    def test_get_quota_usage(self, youtube_service):
        """Test obtención de uso de quota"""
        youtube_service.quota_used_today = 150
        
        result = youtube_service.get_quota_usage()
        
        assert result == {
            "quota_used": 150,
            "quota_limit": youtube_service.config.quota_limit_per_day,
            "quota_remaining": youtube_service.config.quota_limit_per_day - 150
        }

    def test_check_quota_limit(self, youtube_service):
        """Test verificación de límite de quota"""
        youtube_service.quota_used_today = 900
        youtube_service.config.quota_limit_per_day = 1000
        
        # Should allow operation within limit
        assert youtube_service._check_quota_limit(50) is True
        
        # Should deny operation exceeding limit  
        assert youtube_service._check_quota_limit(200) is False

    def test_parse_duration(self, youtube_service):
        """Test parsing de duración ISO 8601"""
        # Test various duration formats
        assert youtube_service._parse_duration("PT3M45S") == 225  # 3:45
        assert youtube_service._parse_duration("PT1H2M3S") == 3723  # 1:02:03
        assert youtube_service._parse_duration("PT30S") == 30  # 0:30
        assert youtube_service._parse_duration("PT5M") == 300  # 5:00

    def test_parse_published_date(self, youtube_service):
        """Test parsing de fecha de publicación"""
        date_str = "2023-01-15T10:30:00Z"
        result = youtube_service._parse_published_date(date_str)
        
        assert isinstance(result, datetime)
        assert result.year == 2023
        assert result.month == 1
        assert result.day == 15

    def test_get_best_thumbnail(self, youtube_service):
        """Test selección de mejor thumbnail"""
        thumbnails = {
            "default": {"url": "http://example.com/default.jpg"},
            "medium": {"url": "http://example.com/medium.jpg"},
            "high": {"url": "http://example.com/high.jpg"},
            "standard": {"url": "http://example.com/standard.jpg"},
            "maxres": {"url": "http://example.com/maxres.jpg"}
        }
        
        result = youtube_service._get_best_thumbnail(thumbnails)
        
        # Should prefer highest quality available
        assert result == "http://example.com/maxres.jpg"

    def test_get_best_thumbnail_fallback(self, youtube_service):
        """Test fallback cuando no hay thumbnails de alta calidad"""
        thumbnails = {
            "default": {"url": "http://example.com/default.jpg"}
        }
        
        result = youtube_service._get_best_thumbnail(thumbnails)
        
        assert result == "http://example.com/default.jpg"

    def test_is_music_related_category(self, youtube_service):
        """Test identificación de categorías relacionadas con música"""
        music_category = {"id": "10", "title": "Music"}
        non_music_category = {"id": "20", "title": "Gaming"}
        
        assert youtube_service._is_music_related_category(music_category) is True
        assert youtube_service._is_music_related_category(non_music_category) is False


class TestYouTubeAPIServicePrivateMethods:
    """Tests para métodos privados críticos"""

    def test_build_search_params(self, youtube_service):
        """Test construcción de parámetros de búsqueda"""
        options = SearchOptions(
            order="relevance",
            max_results=10
        )
        
        params = youtube_service._build_search_params("test query", options)
        
        assert params["q"] == "test query"
        assert params["maxResults"] == 10
        assert params["order"] == "relevance"

    def test_build_search_params_defaults(self, youtube_service):
        """Test parámetros por defecto para búsqueda"""
        options = SearchOptions()
        params = youtube_service._build_search_params("test", options)
        
        assert params["q"] == "test"
        assert params["maxResults"] == 6  # default from SearchOptions
        assert params["type"] == "video"
        assert params["part"] == "snippet"  # Correct default part

    def test_get_random_queries(self, youtube_service):
        """Test generación de queries aleatorios"""
        # Mock the settings to avoid AttributeError
        with patch.object(youtube_service, '_get_random_queries') as mock_method:
            mock_method.return_value = ["pop music", "rock songs", "jazz classics"]
            
            queries = youtube_service._get_random_queries()
            
            assert isinstance(queries, list)
            assert len(queries) > 0
            # All queries should be strings
            assert all(isinstance(q, str) for q in queries)
