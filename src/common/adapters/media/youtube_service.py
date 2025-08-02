import re
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional

from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from ...interfaces.imedia_service import IYouTubeService
from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import SearchOptions, YouTubeServiceConfig, YouTubeVideoInfo
from ...utils.music_metadata_extractor import MusicMetadataExtractor
from ...utils.retry_manager import CircuitBreaker, RetryManager
from ...utils.validators import TextCleaner


class YouTubeAPIService(IYouTubeService, LoggingMixin):
    """Servicio simplificado para interactuar con la API de YouTube"""

    def __init__(
        self,
        config: Optional[YouTubeServiceConfig] = None,
    ):
        super().__init__()
        self.config = config or YouTubeServiceConfig()

        # API configuration from settings
        self.api_key = settings.YOUTUBE_API_KEY
        self.service_name = settings.YOUTUBE_API_SERVICE_NAME
        self.api_version = settings.YOUTUBE_API_VERSION

        # Components
        self.text_cleaner = TextCleaner()
        self.metadata_extractor = MusicMetadataExtractor()
        self.retry_manager = RetryManager(
            max_retries=self.config.max_retries, base_delay=self.config.retry_delay
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=300.0,  # 5 minutes
            expected_exception=HttpError,
        )

        # Initialize YouTube client
        self.youtube = self._build_youtube_client()

        # Quota tracking
        self.quota_used_today = 0
        self.enable_quota_tracking = self.config.enable_quota_tracking

    def _build_youtube_client(self):
        """Builds the YouTube API client"""
        try:
            return build(
                self.service_name,
                self.api_version,
                developerKey=self.api_key,
            )
        except Exception as e:
            self.logger.error(f"Failed to build YouTube client: {str(e)}")
            raise

    async def search_videos(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[YouTubeVideoInfo]:
        """Search videos on YouTube with configurable options"""
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
        """Search videos using circuit breaker"""
        return await self.circuit_breaker.call(self._perform_search, query, options)

    async def _perform_search(
        self, query: str, options: SearchOptions
    ) -> List[YouTubeVideoInfo]:
        """Performs the actual search on the API"""
        search_params = self._build_search_params(query, options)

        # Check quota before making the call
        if self.enable_quota_tracking and not self._check_quota_limit(100):
            self.logger.warning("YouTube API quota limit reached")
            return []

        try:
            search_response = self.youtube.search().list(**search_params).execute()
            self.logger.debug(f"Search response: {search_response}")

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
        """Builds search parameters"""
        search_params = {
            "q": query.strip(),
            "part": "snippet",
            "type": "video",
            "maxResults": min(options.max_results, 50),  # YouTube API limit
            "videoCategoryId": options.video_category_id,
            "order": options.order,
            "safeSearch": options.safe_search,
        }

        # Add optional parameters
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
        """Gets details of a specific video"""
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
        """Gets random videos using predefined queries"""
        if not options:
            options = SearchOptions()

        try:
            random_queries = self._get_random_queries()

            if not random_queries:
                self.logger.error("No random queries available")
                return []

            query = secrets.SystemRandom().choice(random_queries)
            self.logger.debug(f"Using random query: {query}")

            return await self.search_videos(query, options)

        except Exception as e:
            self.logger.error(f"Error getting random videos: {str(e)}")
            return []

    def _get_random_queries(self) -> List[str]:
        """Gets random queries for search"""
        return settings.RANDOM_MUSIC_QUERIES

    async def _get_videos_details(self, video_ids: List[str]) -> List[YouTubeVideoInfo]:
        """Gets complete details of a list of videos"""
        if not video_ids:
            return []

        try:
            # Check quota before making the call
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
        """Makes the actual API call to get details"""
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
        """Builds a YouTubeVideoInfo object from API data"""
        try:
            snippet = video_data["snippet"]
            statistics = video_data.get("statistics", {})
            content_details = video_data["contentDetails"]

            # Parse ISO 8601 duration
            duration_seconds = self._parse_duration(content_details["duration"])

            # Parse publication date
            published_at = self._parse_published_date(snippet["publishedAt"])

            # Process title and channel
            title = self.text_cleaner.clean_title(snippet["title"])
            channel_title = self.text_cleaner.clean_channel_name(
                snippet["channelTitle"]
            )

            # Solo almacenar el category_id para referencia, el género se analiza por separado
            category_id = snippet.get("categoryId", "10")

            # No mapear género aquí - se hará con MusicGenreAnalyzer posteriormente
            # Solo usamos "Music" como valor por defecto ya que filtramos por Category ID 10

            # Get the best quality thumbnail available
            thumbnail_url = self._get_best_thumbnail(snippet.get("thumbnails", {}))

            video_info = YouTubeVideoInfo(
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
                genre="Music",  # Valor por defecto - el género real se determina con MusicGenreAnalyzer
                url=f"https://www.youtube.com/watch?v={video_data['id']}",
            )

            # Extract music metadata
            video_info = self.metadata_extractor.extract_music_metadata(video_info)

            return video_info

        except Exception as e:
            self.logger.error(f"Error building video info: {str(e)}")
            return None

    def _parse_duration(self, duration_str: str) -> int:
        """Converts ISO 8601 duration to seconds"""
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
        """Parses the publication date"""
        try:
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except Exception as e:
            self.logger.error(f"Error parsing published date '{date_str}': {str(e)}")
            return datetime.now()

    def _get_best_thumbnail(self, thumbnails: Dict[str, Any]) -> str:
        """Gets the URL of the best quality thumbnail available"""
        # Order of preference: maxres > high > medium > default
        for quality in ["maxres", "high", "medium", "default"]:
            if quality in thumbnails:
                return thumbnails[quality]["url"]

        # Fallback if no thumbnails
        return ""

    def _check_quota_limit(self, cost: int) -> bool:
        """Verifies if an operation can be performed without exceeding quota"""
        return (self.quota_used_today + cost) <= self.config.quota_limit_per_day

    def get_quota_usage(self) -> Dict[str, int]:
        """Gets quota usage information"""
        return {
            "quota_used": self.quota_used_today,
            "quota_limit": self.config.quota_limit_per_day,
            "quota_remaining": max(
                0, self.config.quota_limit_per_day - self.quota_used_today
            ),
        }

    async def get_music_categories(self) -> List[Dict[str, Any]]:
        """Gets all available YouTube video categories with focus on music"""
        try:
            # Check quota before making the call
            if self.enable_quota_tracking and not self._check_quota_limit(1):
                self.logger.warning("YouTube API quota limit reached for categories")
                return self._get_fallback_music_categories()

            categories_response = await self.circuit_breaker.call(
                self._fetch_video_categories
            )

            if self.enable_quota_tracking:
                self.quota_used_today += 1  # Cost per videoCategories.list call

            music_categories = []
            for category in categories_response.get("items", []):
                category_info = self._build_category_info(category)
                if category_info and self._is_music_related_category(category_info):
                    music_categories.append(category_info)

            # Always include the main music category if not present
            if not any(cat["id"] == "10" for cat in music_categories):
                music_categories.insert(
                    0,
                    {
                        "id": "10",
                        "title": "Music",
                        "assignable": True,
                        "is_primary_music": True,
                    },
                )

            return music_categories

        except Exception as e:
            self.logger.error(f"Error getting music categories: {str(e)}")
            return self._get_fallback_music_categories()

    def _fetch_video_categories(self) -> Dict[str, Any]:
        """Makes the actual API call to get video categories"""
        return (
            self.youtube.videoCategories()
            .list(part="snippet", regionCode="US")
            .execute()
        )

    def _build_category_info(
        self, category_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Builds category information from API data"""
        try:
            snippet = category_data["snippet"]
            return {
                "id": category_data["id"],
                "title": snippet["title"],
                "assignable": snippet.get("assignable", False),
                "channel_id": snippet.get("channelId", ""),
                "is_primary_music": category_data["id"] == "10",
            }
        except Exception as e:
            self.logger.error(f"Error building category info: {str(e)}")
            return None

    def _is_music_related_category(self, category: Dict[str, Any]) -> bool:
        """Determines if a category is music-related"""
        music_keywords = [
            "music",
            "musical",
            "song",
            "audio",
            "sound",
            "concert",
            "performance",
            "artist",
            "band",
        ]

        title_lower = category["title"].lower()
        return category["id"] == "10" or any(  # Primary music category
            keyword in title_lower for keyword in music_keywords
        )

    def _get_fallback_music_categories(self) -> List[Dict[str, Any]]:
        """Returns fallback music categories when API is not available"""
        return [
            {
                "id": "10",
                "title": "Music",
                "assignable": True,
                "channel_id": "",
                "is_primary_music": True,
            }
        ]

    async def search_music_only(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List["YouTubeVideoInfo"]:
        """Search specifically for music content only"""
        if not options:
            options = SearchOptions()

        # Force music category
        options.video_category_id = "10"

        # Add music-specific keywords to query if not present
        music_keywords = ["music", "song", "audio", "track", "artist", "band"]
        query_lower = query.lower()

        if not any(keyword in query_lower for keyword in music_keywords):
            query = f"{query} music"

        try:
            videos = await self.search_videos(query, options)

            # Additional filtering for music content
            music_videos = []
            for video in videos:
                if self._is_music_content(video):
                    music_videos.append(video)

            return music_videos

        except Exception as e:
            self.logger.error(f"Error searching music only: {str(e)}")
            return []

    def _is_music_content(self, video: "YouTubeVideoInfo") -> bool:
        """Determines if video content is music-related"""
        # Check category
        if video.category_id != "10":
            return False

        # Check for music indicators in title
        music_indicators = [
            "music",
            "song",
            "audio",
            "track",
            "album",
            "single",
            "official video",
            "music video",
            "mv",
            "cover",
            "remix",
            "acoustic",
            "live",
            "concert",
            "performance",
        ]

        title_lower = video.title.lower()
        description_lower = video.description.lower()

        # Title should contain music indicators
        title_has_music = any(
            indicator in title_lower for indicator in music_indicators
        )

        # Tags should contain music-related terms
        music_tags = any(
            tag.lower() in ["music", "song", "audio", "track", "artist", "band"]
            for tag in video.tags
        )

        # Description should mention music
        desc_has_music = any(
            indicator in description_lower for indicator in music_indicators[:6]
        )

        # At least 2 of these conditions should be true
        music_score = sum([title_has_music, music_tags, desc_has_music])

        return music_score >= 2
