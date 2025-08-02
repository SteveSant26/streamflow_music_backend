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
from ...utils.music_metadata_extractor import MusicMetadataExtractor
from ...utils.retry_manager import CircuitBreaker, RetryManager
from ...utils.validators import TextCleaner, URLValidator


class YouTubeAPIService(IYouTubeService, LoggingMixin):
    """Servicio mejorado para interactuar con la API de YouTube"""

    def __init__(
        self,
        config: Optional[YouTubeServiceConfig] = None,
    ):
        super().__init__()
        self.config = config or YouTubeServiceConfig()

        # Use API key from settings
        self.api_key = settings.YOUTUBE_API_KEY
        self.service_name = settings.YOUTUBE_API_SERVICE_NAME
        self.api_version = settings.YOUTUBE_API_VERSION

        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY must be set in Django settings")

        # Componentes auxiliares
        self.text_cleaner = TextCleaner()
        self.url_validator = URLValidator()
        self.metadata_extractor = MusicMetadataExtractor()
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
                genre=genre,
                url=f"https://www.youtube.com/watch?v={video_data['id']}",
            )

            # Extraer metadatos musicales (artistas y álbumes)
            video_info = self.metadata_extractor.extract_music_metadata(video_info)

            return video_info

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
        categories = getattr(settings, "YOUTUBE_CATEGORIES", {})

        try:
            # Try with integer key first (as defined in settings)
            category_int = int(category_id)
            if category_int in categories:
                return categories[category_int]

            # Fallback to string key for backward compatibility
            if str(category_id) in categories:
                return categories[str(category_id)]

            return "Music"  # Default fallback
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

    async def get_enriched_random_videos(
        self, options: Optional[SearchOptions] = None
    ) -> List[YouTubeVideoInfo]:
        """
        Obtiene videos aleatorios con metadatos musicales extraídos

        Returns:
            Lista de videos con información de artistas y álbumes extraída
        """
        videos = await self.get_random_videos(options)
        return self._enrich_videos_with_music_data(videos)

    async def search_videos_with_music_metadata(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[YouTubeVideoInfo]:
        """
        Busca videos y extrae metadatos musicales

        Args:
            query: Consulta de búsqueda
            options: Opciones de búsqueda

        Returns:
            Lista de videos con metadatos musicales extraídos
        """
        videos = await self.search_videos(query, options)
        return self._enrich_videos_with_music_data(videos)

    def _enrich_videos_with_music_data(
        self, videos: List[YouTubeVideoInfo]
    ) -> List[YouTubeVideoInfo]:
        """
        Enriquece videos con datos musicales adicionales

        Args:
            videos: Lista de videos a enriquecer

        Returns:
            Videos con datos musicales enriquecidos
        """
        enriched_videos = []

        for video in videos:
            try:
                # Los metadatos ya se extraen en _build_video_info,
                # pero aquí podemos hacer procesamiento adicional
                enriched_video = self._add_music_insights(video)
                enriched_videos.append(enriched_video)

            except Exception as e:
                self.logger.error(f"Error enriching video {video.video_id}: {str(e)}")
                # Agregar el video sin enriquecimiento
                enriched_videos.append(video)

        return enriched_videos

    def _add_music_insights(self, video: YouTubeVideoInfo) -> YouTubeVideoInfo:
        """
        Agrega insights musicales adicionales al video

        Args:
            video: Video a enriquecer

        Returns:
            Video con insights adicionales
        """
        try:
            # Agregar información contextual
            if video.extracted_artists:
                main_artist = video.extracted_artists[0]
                self.logger.debug(
                    f"Main artist for video {video.video_id}: {main_artist.name}"
                )

                # Agregar información adicional al artista principal
                if main_artist.additional_info is None:
                    main_artist.additional_info = {}

                main_artist.additional_info.update(
                    {
                        "video_genre": video.genre,
                        "video_category": video.category_id,
                        "channel_match": main_artist.channel_id == video.channel_id,
                    }
                )

            if video.extracted_albums:
                main_album = video.extracted_albums[0]
                self.logger.debug(
                    f"Main album for video {video.video_id}: {main_album.title}"
                )

                # Agregar información contextual al álbum
                if main_album.additional_info is None:
                    main_album.additional_info = {}

                main_album.additional_info.update(
                    {
                        "video_published_year": video.published_at.year,
                        "estimated_album_track": (
                            True if main_album.confidence_score > 0.5 else False
                        ),
                    }
                )

            return video

        except Exception as e:
            self.logger.error(
                f"Error adding music insights to video {video.video_id}: {str(e)}"
            )
            return video

    def get_extracted_artists_summary(
        self, videos: List[YouTubeVideoInfo]
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de todos los artistas extraídos

        Args:
            videos: Lista de videos con metadatos extraídos

        Returns:
            Resumen de artistas con estadísticas
        """
        artists_data: Dict[str, Dict[str, Any]] = {}
        total_extractions = 0

        for video in videos:
            if video.extracted_artists:
                total_extractions += len(video.extracted_artists)

                for artist in video.extracted_artists:
                    if artist.name not in artists_data:
                        artists_data[artist.name] = {
                            "name": artist.name,
                            "appearances": 0,
                            "total_confidence": 0.0,
                            "sources": set(),
                            "videos": [],
                            "channel_ids": set(),
                        }

                    artist_data = artists_data[artist.name]
                    artist_data["appearances"] += 1
                    artist_data["total_confidence"] += artist.confidence_score
                    artist_data["sources"].add(artist.extracted_from)
                    artist_data["videos"].append(
                        {
                            "video_id": video.video_id,
                            "title": video.title,
                            "confidence": artist.confidence_score,
                        }
                    )

                    if artist.channel_id:
                        artist_data["channel_ids"].add(artist.channel_id)

        # Calcular estadísticas finales
        for artist_name, data in artists_data.items():
            data["average_confidence"] = data["total_confidence"] / data["appearances"]
            data["sources"] = list(data["sources"])
            data["channel_ids"] = list(data["channel_ids"])
            data["is_likely_main_artist"] = data["average_confidence"] > 0.6

        # Ordenar por confianza
        sorted_artists = sorted(
            artists_data.items(),
            key=lambda item: float(item[1]["average_confidence"]),
            reverse=True,
        )

        return {
            "total_videos": len(videos),
            "total_artist_extractions": total_extractions,
            "unique_artists": len(artists_data),
            "artists": dict(sorted_artists),
        }

    def get_extracted_albums_summary(
        self, videos: List[YouTubeVideoInfo]
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de todos los álbumes extraídos

        Args:
            videos: Lista de videos con metadatos extraídos

        Returns:
            Resumen de álbumes con estadísticas
        """
        albums_data: Dict[str, Dict[str, Any]] = {}
        total_extractions = 0

        for video in videos:
            if video.extracted_albums:
                total_extractions += len(video.extracted_albums)

                for album in video.extracted_albums:
                    album_key = f"{album.title}||{album.artist_name or 'Unknown'}"

                    if album_key not in albums_data:
                        albums_data[album_key] = {
                            "title": album.title,
                            "artist_name": album.artist_name,
                            "appearances": 0,
                            "total_confidence": 0.0,
                            "sources": set(),
                            "videos": [],
                            "release_years": set(),
                        }

                    album_data = albums_data[album_key]
                    album_data["appearances"] += 1
                    album_data["total_confidence"] += album.confidence_score
                    album_data["sources"].add(album.extracted_from)
                    album_data["videos"].append(
                        {
                            "video_id": video.video_id,
                            "title": video.title,
                            "confidence": album.confidence_score,
                        }
                    )

                    if album.release_year:
                        album_data["release_years"].add(album.release_year)

        # Calcular estadísticas finales
        for album_key, data in albums_data.items():
            data["average_confidence"] = data["total_confidence"] / data["appearances"]
            data["sources"] = list(data["sources"])
            data["release_years"] = list(data["release_years"])
            data["estimated_release_year"] = (
                max(data["release_years"]) if data["release_years"] else None
            )
            data["is_likely_album_track"] = data["average_confidence"] > 0.5

        # Ordenar por confianza
        sorted_albums = sorted(
            albums_data.items(),
            key=lambda item: float(item[1]["average_confidence"]),
            reverse=True,
        )

        return {
            "total_videos": len(videos),
            "total_album_extractions": total_extractions,
            "unique_albums": len(albums_data),
            "albums": dict(sorted_albums),
        }
