from datetime import datetime
from typing import Any, Dict, List, Optional

from ...interfaces.imedia_service import IMusicService
from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import (
    AudioTrackData,
    DownloadOptions,
    MusicServiceConfig,
    SearchOptions,
    VideoInfo,
    YouTubeVideoInfo,
)
from ...utils.music_metadata_extractor import MusicMetadataExtractor
from .audio_download_service import AudioDownloadService
from .youtube_service import YouTubeAPIService


class UnifiedMusicService(IMusicService, LoggingMixin):
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB

    def __init__(
        self,
        config: Optional[MusicServiceConfig] = None,
        youtube_service: Optional[YouTubeAPIService] = None,
        audio_service: Optional[AudioDownloadService] = None,
    ):
        super().__init__()
        self.config = config or MusicServiceConfig()

        self.youtube_service = youtube_service or YouTubeAPIService()
        self.audio_service = audio_service or AudioDownloadService()
        self.metadata_extractor = MusicMetadataExtractor()

        self.artist_repository = None
        self.album_repository = None

        self._metrics = {
            "searches_performed": 0,
            "videos_processed": 0,
            "audio_downloads": 0,
            "metadata_extractions": 0,
            "errors": 0,
            "videos_filtered_by_size": 0,
        }

    def configure_repositories(self, artist_repository: Any, album_repository: Any):
        self.artist_repository = artist_repository
        self.album_repository = album_repository

    def _check_file_size_before_processing(self, video_id: str) -> bool:
        try:
            url = f"https://www.youtube.com/watch?v={video_id}"
            audio_info = self.audio_service.get_audio_info(url)

            if not audio_info:
                self.logger.warning(
                    f"No se pudo obtener información del archivo para video {video_id}"
                )
                return False

            audio_formats = audio_info.get("formats", [])

            for format_info in audio_formats:
                filesize = format_info.get("filesize")
                if filesize and filesize > self.MAX_FILE_SIZE_BYTES:
                    self.logger.info(
                        f"Video {video_id} excede el límite de tamaño: "
                        f"{filesize / (1024 * 1024):.2f}MB > {self.MAX_FILE_SIZE_BYTES / (1024 * 1024)}MB"
                    )
                    self._metrics["videos_filtered_by_size"] += 1
                    return False

            return True

        except Exception as e:
            self.logger.error(
                f"Error verificando tamaño del archivo para video {video_id}: {str(e)}"
            )
            return True

    def _filter_videos_by_size(
        self, videos: List[YouTubeVideoInfo]
    ) -> List[YouTubeVideoInfo]:
        filtered_videos = []

        for video in videos:
            try:
                if self._check_file_size_before_processing(video.video_id):
                    filtered_videos.append(video)
                else:
                    self.logger.info(
                        f"Video filtrado por tamaño: {video.title} ({video.video_id})"
                    )
            except Exception as e:
                self.logger.error(f"Error filtrando video {video.video_id}: {str(e)}")
                filtered_videos.append(video)

        if len(filtered_videos) != len(videos):
            self.logger.info(
                f"Filtrados {len(videos) - len(filtered_videos)} videos de {len(videos)} por tamaño"
            )

        return filtered_videos

    def search_and_process_audio(
        self,
        query: str,
        options: Optional[SearchOptions] = None,
        download_audio: bool = False,
        extract_metadata: bool = True,
    ) -> List[AudioTrackData]:
        try:
            self._metrics["searches_performed"] += 1

            videos = self._search_videos_with_metadata(query, options, extract_metadata)

            if not videos:
                self.logger.warning(f"No videos found for query: {query}")
                return []

            filtered_videos = self._filter_videos_by_size(videos)

            if not filtered_videos:
                self.logger.warning(f"No videos passed size filter for query: {query}")
                return []

            audio_tracks = []
            for video in filtered_videos:
                try:
                    track = self._process_video_to_audio_track(
                        video, download_audio=download_audio, skip_size_check=True
                    )
                    if track:
                        audio_tracks.append(track)
                        self._metrics["videos_processed"] += 1

                except Exception as e:
                    self.logger.error(
                        f"Error processing video {video.video_id}: {str(e)}"
                    )
                    self._metrics["errors"] += 1

            self.logger.info(
                f"Processed {len(audio_tracks)} tracks from query '{query}' "
                f"({len(videos) - len(filtered_videos)} filtered by size)"
            )
            return audio_tracks

        except Exception as e:
            self.logger.error(f"Error in search_and_process_audio: {str(e)}")
            self._metrics["errors"] += 1
            return []

    def get_random_music(
        self,
        options: Optional[SearchOptions] = None,
        download_audio: bool = False,
        extract_metadata: bool = True,
    ) -> List[AudioTrackData]:
        try:
            videos = self._get_random_videos_with_metadata(options, extract_metadata)

            if not videos:
                self.logger.warning("No random videos obtained")
                return []

            filtered_videos = self._filter_videos_by_size(videos)

            if not filtered_videos:
                self.logger.warning("No random videos passed size filter")
                return []

            audio_tracks = []
            for video in filtered_videos:
                try:
                    track = self._process_video_to_audio_track(
                        video, download_audio=download_audio, skip_size_check=True
                    )
                    if track:
                        audio_tracks.append(track)

                except Exception as e:
                    self.logger.error(
                        f"Error processing random video {video.video_id}: {str(e)}"
                    )

            self.logger.info(
                f"Processed {len(audio_tracks)} random tracks "
                f"({len(videos) - len(filtered_videos)} filtered by size)"
            )
            return audio_tracks

        except Exception as e:
            self.logger.error(f"Error getting random music: {str(e)}")
            return []

    def download_audio_from_video(
        self, video_id: str, options: Optional[DownloadOptions] = None
    ) -> Optional[bytes]:
        try:
            if not self._check_file_size_before_processing(video_id):
                self.logger.info(
                    f"Video {video_id} no descargado: excede límite de tamaño"
                )
                return None

            self._metrics["audio_downloads"] += 1
            url = f"https://www.youtube.com/watch?v={video_id}"

            download_options = options or DownloadOptions()
            if download_options.max_filesize is None:
                download_options.max_filesize = self.MAX_FILE_SIZE_BYTES

            return self.audio_service.download_audio(url, download_options)

        except Exception as e:
            self.logger.error(f"Error downloading audio for video {video_id}: {str(e)}")
            self._metrics["errors"] += 1
            return None

    def _search_videos_with_metadata(
        self,
        query: str,
        options: Optional[SearchOptions],
        extract_metadata: bool = True,
    ) -> List[YouTubeVideoInfo]:
        videos = self.youtube_service.search_videos(query, options)

        if extract_metadata and videos:
            self._metrics["metadata_extractions"] += len(videos)
            return [
                self.metadata_extractor.extract_music_metadata(video)
                for video in videos
            ]

        return videos

    def _get_random_videos_with_metadata(
        self, options: Optional[SearchOptions], extract_metadata: bool = True
    ) -> List[YouTubeVideoInfo]:
        videos = self.youtube_service.get_random_videos(options)

        if extract_metadata and videos:
            self._metrics["metadata_extractions"] += len(videos)
            return [
                self.metadata_extractor.extract_music_metadata(video)
                for video in videos
            ]

        return videos

    def _process_video_to_audio_track(
        self,
        video: YouTubeVideoInfo,
        download_audio: bool = False,
        skip_size_check: bool = False,
    ) -> Optional[AudioTrackData]:
        try:
            if not skip_size_check and not self._check_file_size_before_processing(
                video.video_id
            ):
                self.logger.info(f"Video {video.video_id} filtrado por tamaño excesivo")
                return None

            main_artist = "Unknown Artist"
            if video.extracted_artists:
                main_artist = video.extracted_artists[0].name
            else:
                main_artist = video.channel_title

            album_title = None
            if video.extracted_albums:
                album_title = video.extracted_albums[0].title

            audio_data = None
            audio_filename = None
            if download_audio:
                download_options = DownloadOptions(
                    max_filesize=self.MAX_FILE_SIZE_BYTES
                )
                audio_data = self.audio_service.download_audio(
                    f"https://www.youtube.com/watch?v={video.video_id}",
                    download_options,
                )
                if audio_data:
                    audio_filename = f"{video.video_id}.mp3"

            return AudioTrackData(
                video_id=video.video_id,
                title=video.title,
                artist_name=main_artist,
                album_title=album_title,
                duration_seconds=video.duration_seconds,
                thumbnail_url=video.thumbnail_url,
                genre=video.genre,
                tags=video.tags,
                url=video.url,
                audio_file_data=audio_data,
                audio_file_name=audio_filename,
                extracted_artists=video.extracted_artists,
                extracted_albums=video.extracted_albums,
            )

        except Exception as e:
            self.logger.error(f"Error converting video to audio track: {str(e)}")
            return None

    def get_service_metrics(self) -> Dict[str, Any]:
        return {
            **self._metrics,
            "max_file_size_mb": self.MAX_FILE_SIZE_BYTES / (1024 * 1024),
            "youtube_quota_usage": (
                self.youtube_service.get_quota_usage()
                if hasattr(self.youtube_service, "get_quota_usage")
                else {}
            ),
            "service_uptime": "N/A",
            "last_activity": datetime.now().isoformat(),
        }

    def cleanup(self):
        try:
            self.audio_service.cleanup()

            self._metrics = {
                "searches_performed": 0,
                "videos_processed": 0,
                "audio_downloads": 0,
                "metadata_extractions": 0,
                "errors": 0,
                "videos_filtered_by_size": 0,
            }

            self.logger.info("UnifiedMusicService cleanup completed")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")

    def get_random_music_tracks(self, max_results: int = 6) -> List[AudioTrackData]:
        options = SearchOptions(max_results=max_results)
        return self.get_random_music(options, download_audio=False)

    def search_and_process_music(
        self, query: str, max_results: int = 6
    ) -> List[AudioTrackData]:
        options = SearchOptions(max_results=max_results)
        return self.search_and_process_audio(query, options, download_audio=False)

    def search_music_tracks(
        self, query: str, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        return self.search_and_process_audio(query, options, download_audio=False)

    def get_music_track_details(self, track_id: str) -> Optional[AudioTrackData]:
        try:
            video = self.youtube_service.get_video_details(track_id)
            if video:
                video_with_metadata = self.metadata_extractor.extract_music_metadata(
                    video
                )
                return self._process_video_to_audio_track(video_with_metadata)
            return None
        except Exception as e:
            self.logger.error(f"Error getting track details for {track_id}: {str(e)}")
            return None

    def get_random_audio_tracks(
        self, options: Optional[SearchOptions] = None
    ) -> List[AudioTrackData]:
        return self.get_random_music(options, download_audio=False)

    def process_video_to_audio_track(
        self, video_info: VideoInfo
    ) -> Optional[AudioTrackData]:
        try:
            if isinstance(video_info, YouTubeVideoInfo):
                youtube_video = video_info
            else:
                youtube_video = YouTubeVideoInfo(
                    video_id=video_info.video_id,
                    title=video_info.title,
                    channel_title=video_info.channel_title,
                    channel_id=video_info.channel_id,
                    thumbnail_url=video_info.thumbnail_url,
                    description=video_info.description,
                    duration_seconds=video_info.duration_seconds,
                    published_at=video_info.published_at,
                    view_count=video_info.view_count,
                    like_count=video_info.like_count,
                    tags=video_info.tags,
                    category_id=video_info.category_id,
                    genre=video_info.genre,
                    url=video_info.url,
                )

            if (
                not youtube_video.extracted_artists
                and not youtube_video.extracted_albums
            ):
                youtube_video = self.metadata_extractor.extract_music_metadata(
                    youtube_video
                )

            return self._process_video_to_audio_track(
                youtube_video, download_audio=False, skip_size_check=False
            )
        except Exception as e:
            self.logger.error(f"Error processing video to audio track: {str(e)}")
            return None
