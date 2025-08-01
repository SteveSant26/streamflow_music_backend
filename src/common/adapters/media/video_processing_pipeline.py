"""
Pipeline para procesamiento de videos y generación de tracks
"""
import asyncio
from typing import List, Optional, Protocol, Sequence

from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import AudioTrackData, VideoInfo
from ...utils.retry_manager import RetryManager


class VideoProcessor(Protocol):
    """Protocol para procesadores de video"""

    async def process(self, video_info: VideoInfo) -> Optional[AudioTrackData]:
        """Procesa un video y retorna datos de audio track"""
        ...


class VideoProcessingPipeline(LoggingMixin):
    """Pipeline configurable para procesamiento de videos"""

    def __init__(
        self,
        processor: VideoProcessor,
        retry_manager: RetryManager,
        max_concurrent: int = 3,
        enable_detailed_logging: bool = False,
    ):
        super().__init__()
        self.processor = processor
        self.retry_manager = retry_manager
        self.max_concurrent = max_concurrent
        self.enable_detailed_logging = enable_detailed_logging

    async def process_videos(self, videos: Sequence[VideoInfo]) -> List[AudioTrackData]:
        """Procesa una lista de videos en paralelo"""
        if not videos:
            self.logger.info("No videos to process")
            return []

        self.logger.info(f"Starting processing of {len(videos)} videos")

        # Crear semáforo para limitar concurrencia
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def process_with_semaphore(video: VideoInfo) -> Optional[AudioTrackData]:
            async with semaphore:
                try:
                    if self.enable_detailed_logging:
                        self.logger.debug(f"Processing video: {video.video_id}")

                    result = await self.retry_manager.execute_with_retry(
                        self.processor.process, video
                    )

                    if self.enable_detailed_logging:
                        success = "successfully" if result else "failed"
                        self.logger.debug(f"Video {video.video_id} processed {success}")

                    return result

                except Exception as e:
                    self.logger.error(
                        f"Failed to process video {video.video_id}: {str(e)}"
                    )
                    return None

        # Ejecutar tareas en paralelo
        tasks = [process_with_semaphore(video) for video in videos]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar y recopilar resultados exitosos
        processed_tracks = []
        for i, result in enumerate(results):
            if isinstance(result, AudioTrackData):
                processed_tracks.append(result)
            elif isinstance(result, Exception):
                self.logger.error(
                    f"Exception processing video {videos[i].video_id}: {str(result)}"
                )

        success_rate = len(processed_tracks) / len(videos) * 100
        self.logger.info(
            f"Processing completed: {len(processed_tracks)}/{len(videos)} videos "
            f"({success_rate:.1f}% success rate)"
        )

        return processed_tracks

    async def process_single_video(self, video: VideoInfo) -> Optional[AudioTrackData]:
        """Procesa un solo video"""
        try:
            return await self.retry_manager.execute_with_retry(
                self.processor.process, video
            )
        except Exception as e:
            self.logger.error(f"Failed to process video {video.video_id}: {str(e)}")
            return None
