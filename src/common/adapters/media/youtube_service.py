"""
Servicio mejorado para interactuar con la API de YouTube
"""

import random
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...interfaces.imedia_service import IYouTubeService
from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import SearchOptions, YouTubeServiceConfig, YouTubeVideoInfo
from ...utils.retry_manager import CircuitBreaker, RetryManager
from ...utils.validators import TextCleaner, URLValidator


class YouTubeAPIService(IYouTubeService, LoggingMixin):
    """Servicio mejorado para interactuar con la API de YouTube"""

    def __init__(
        self,
        config: Optional[YouTubeServiceConfig] = None,
        api_key: Optional[str] = None,
    ):
        super().__init__()
        self.config = config or YouTubeServiceConfig()
        self.api_key = api_key or self.config.api_key or settings.YOUTUBE_API_KEY

        # Componentes auxiliares
        self.text_cleaner = TextCleaner()
        self.url_validator = URLValidator()
        self.retry_manager = RetryManager(
            max_retries=self.config.max_retries, base_delay=self.config.retry_delay
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=300.0,  # 5 minutes
            expected_exception=HttpError,
        )

        # Inicializar cliente de YouTube
        self.youtube = self._build_youtube_client()

        # Tracking de cuota (si está habilitado)
        self.quota_used_today = 0
        self.enable_quota_tracking = self.config.enable_quota_tracking

    def _build_youtube_client(self):
        """Construye el cliente de YouTube API"""
        try:
            return build(
                self.config.service_name,
                self.config.api_version,
                developerKey=self.api_key,
            )
        except Exception as e:
            self.logger.error(f"Failed to build YouTube client: {str(e)}")
            raise

    async def search_videos(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[YouTubeVideoInfo]:
        """Busca videos en YouTube con opciones configurables"""
        if not query or not query.strip():
            self.logger.warning("Empty search query provided")
            return []

        if not options:
            options = SearchOptions()

        try:
            return (
                await self.retry_manager.execute_with_retry(
                    self._search_videos_with_circuit_breaker, query, options
                )
                or []
            )

        except Exception as e:
            self.logger.error(f"Error searching videos with query '{query}': {str(e)}")
            return []

    async def _search_videos_with_circuit_breaker(
        self, query: str, options: SearchOptions
    ) -> List[YouTubeVideoInfo]:
        """Busca videos usando circuit breaker"""
        return await self.circuit_breaker.call(self._perform_search, query, options)

    async def _perform_search(
        self, query: str, options: SearchOptions
    ) -> List[YouTubeVideoInfo]:
        """Realiza la búsqueda real en la API"""
        search_params = self._build_search_params(query, options)

        # Verificar cuota antes de hacer la llamada
        if self.enable_quota_tracking and not self._check_quota_limit(100):
            self.logger.warning("YouTube API quota limit reached")
            return []

        try:
            search_response = self.youtube.search().list(**search_params).execute()

            if self.enable_quota_tracking:
                self.quota_used_today += 100  # Cost of search operation

            video_ids = [
                item["id"]["videoId"]
                for item in search_response.get("items", [])
                if item.get("id", {}).get("kind") == "youtube#video"
            ]

            if not video_ids:
                self.logger.warning(f"No videos found for query: {query}")
                return []

            return await self._get_videos_details(video_ids)

        except HttpError as e:
            if e.resp.status == 403:  # Quota exceeded
                self.logger.error("YouTube API quota exceeded")
                if self.enable_quota_tracking:
                    self.quota_used_today = self.config.quota_limit_per_day
            raise e

    def _build_search_params(
        self, query: str, options: SearchOptions
    ) -> Dict[str, Any]:
        """Construye los parámetros de búsqueda"""
        search_params = {
            "q": query.strip(),
            "part": "snippet",
            "type": "video",
            "maxResults": min(options.max_results, 50),  # YouTube API limit
            "videoCategoryId": options.video_category_id,
            "order": options.order,
            "safeSearch": options.safe_search,
        }

        # Agregar parámetros opcionales
        if options.region_code:
            search_params["regionCode"] = options.region_code
        if options.language:
            search_params["relevanceLanguage"] = options.language
        if options.published_after:
            search_params["publishedAfter"] = options.published_after.isoformat()
        if options.published_before:
            search_params["publishedBefore"] = options.published_before.isoformat()

        return search_params

    async def get_video_details(self, video_id: str) -> Optional[YouTubeVideoInfo]:
        """Obtiene detalles de un video específico"""
        if not video_id or not isinstance(video_id, str):
            self.logger.error("Invalid video ID provided")
            return None

        try:
            videos = await self._get_videos_details([video_id])
            return videos[0] if videos else None

        except Exception as e:
            self.logger.error(f"Error getting video details for {video_id}: {str(e)}")
            return None

    async def get_random_videos(
        self, options: Optional[SearchOptions] = None
    ) -> List[YouTubeVideoInfo]:
        """Obtiene videos aleatorios usando consultas predefinidas"""
        if not options:
            options = SearchOptions()

        try:
            random_queries = self._get_random_queries()

            if not random_queries:
                self.logger.warning("No random queries available")
                return []

            query = random.choice(random_queries)  # nosec B311
            self.logger.debug(f"Using random query: {query}")

            return await self.search_videos(query, options)

        except Exception as e:
            self.logger.error(f"Error getting random videos: {str(e)}")
            return []

    def _get_random_queries(self) -> List[str]:
        """Obtiene consultas aleatorias para búsqueda"""
        return getattr(
            settings,
            "RANDOM_MUSIC_QUERIES",
            [
                "popular music 2024",
                "trending songs",
                "best music hits",
                "top 40 music",
                "latest music videos",
                "new releases music",
                "acoustic songs",
                "rock music",
                "pop hits",
                "indie music",
            ],
        )

    async def _get_videos_details(self, video_ids: List[str]) -> List[YouTubeVideoInfo]:
        """Obtiene detalles completos de una lista de videos"""
        if not video_ids:
            return []

        try:
            # Verificar cuota antes de hacer la llamada
            if self.enable_quota_tracking and not self._check_quota_limit(1):
                self.logger.warning("YouTube API quota limit reached for video details")
                return []

            videos_response = await self.circuit_breaker.call(
                self._fetch_videos_details, video_ids
            )

            if self.enable_quota_tracking:
                self.quota_used_today += 1  # Cost per videos.list call

            videos = []
            for video_data in videos_response.get("items", []):
                video_info = self._build_video_info(video_data)
                if video_info:
                    videos.append(video_info)

            return videos

        except Exception as e:
            self.logger.error(f"Error getting videos details: {str(e)}")
            return []

    def _fetch_videos_details(self, video_ids: List[str]) -> Dict[str, Any]:
        """Realiza la llamada real a la API para obtener detalles"""
        return (
            self.youtube.videos()
            .list(
                part="snippet,statistics,contentDetails",
                id=",".join(video_ids[:50]),  # API limit
            )
            .execute()
        )

    def _build_video_info(
        self, video_data: Dict[str, Any]
    ) -> Optional[YouTubeVideoInfo]:
        """Construye un objeto YouTubeVideoInfo a partir de datos de la API"""
        try:
            snippet = video_data["snippet"]
            statistics = video_data.get("statistics", {})
            content_details = video_data["contentDetails"]

            # Parsear duración ISO 8601
            duration_seconds = self._parse_duration(content_details["duration"])

            # Parsear fecha de publicación
            published_at = self._parse_published_date(snippet["publishedAt"])

            # Procesar título y canal
            title = self.text_cleaner.clean_title(snippet["title"])
            channel_title = self.text_cleaner.clean_channel_name(
                snippet["channelTitle"]
            )

            # Obtener género basado en categoría
            category_id = snippet.get("categoryId", "10")
            genre = self._get_genre_from_category(category_id)

            # Obtener la mejor calidad de thumbnail disponible
            thumbnail_url = self._get_best_thumbnail(snippet.get("thumbnails", {}))

            return YouTubeVideoInfo(
                video_id=video_data["id"],
                title=title,
                channel_title=channel_title,
                channel_id=snippet["channelId"],
                thumbnail_url=thumbnail_url,
                description=snippet.get("description", ""),
                duration_seconds=duration_seconds,
                published_at=published_at,
                view_count=int(statistics.get("viewCount", 0)),
                like_count=int(statistics.get("likeCount", 0)),
                tags=snippet.get("tags", []),
                category_id=category_id,
                genre=genre,
                url=f"https://www.youtube.com/watch?v={video_data['id']}",
            )

        except Exception as e:
            self.logger.error(f"Error building video info: {str(e)}")
            return None

    def _parse_duration(self, duration_str: str) -> int:
        """Convierte duración ISO 8601 a segundos"""
        try:
            match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration_str)
            if not match:
                return 0

            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            seconds = int(match.group(3)) if match.group(3) else 0

            return hours * 3600 + minutes * 60 + seconds

        except Exception as e:
            self.logger.error(f"Error parsing duration '{duration_str}': {str(e)}")
            return 0

    def _parse_published_date(self, date_str: str) -> datetime:
        """Parsea la fecha de publicación"""
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception as e:
            self.logger.error(f"Error parsing published date '{date_str}': {str(e)}")
            return datetime.now()

    def _get_genre_from_category(self, category_id: str) -> str:
        """Obtiene el género basado en la categoría de YouTube"""
        categories = getattr(
            settings,
            "YOUTUBE_CATEGORIES",
            {
                "10": "Music",
                "1": "Film & Animation",
                "2": "Autos & Vehicles",
                "15": "Pets & Animals",
                "17": "Sports",
                "19": "Travel & Events",
                "20": "Gaming",
                "22": "People & Blogs",
                "23": "Comedy",
                "24": "Entertainment",
                "25": "News & Politics",
                "26": "Howto & Style",
                "27": "Education",
                "28": "Science & Technology",
            },
        )

        try:
            return categories.get(str(category_id), "Music")
        except (ValueError, TypeError):
            return "Music"

    def _get_best_thumbnail(self, thumbnails: Dict[str, Any]) -> str:
        """Obtiene la URL del thumbnail de mejor calidad disponible"""
        # Orden de preferencia: maxres > high > medium > default
        for quality in ["maxres", "high", "medium", "default"]:
            if quality in thumbnails:
                return thumbnails[quality]["url"]

        # Fallback si no hay thumbnails
        return ""

    def _check_quota_limit(self, cost: int) -> bool:
        """Verifica si se puede realizar una operación sin exceder la cuota"""
        return (self.quota_used_today + cost) <= self.config.quota_limit_per_day

    def get_quota_usage(self) -> Dict[str, int]:
        """Obtiene información sobre el uso de cuota"""
        return {
            "quota_used": self.quota_used_today,
            "quota_limit": self.config.quota_limit_per_day,
            "quota_remaining": max(
                0, self.config.quota_limit_per_day - self.quota_used_today
            ),
        }
