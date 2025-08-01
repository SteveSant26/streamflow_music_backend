"""
Servicio mejorado para descarga de audio desde videos
"""
import asyncio
import os
import tempfile
import uuid
from typing import Any, Dict, Optional

import yt_dlp

from ...interfaces.imedia_service import IAudioDownloadService
from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import DownloadOptions


class AudioDownloadService(IAudioDownloadService, LoggingMixin):
    """Servicio mejorado para descargar audio desde videos"""

    def __init__(self, default_options: Optional[DownloadOptions] = None):
        super().__init__()
        self.default_options = default_options or DownloadOptions()
        self._base_ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "writesubtitles": False,
            "writeautomaticsub": False,
            "referer": "https://www.youtube.com/",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }

    async def download_audio(
        self, video_url: str, options: Optional[DownloadOptions] = None
    ) -> Optional[bytes]:
        """Descarga el audio de un video como bytes"""
        if not await self.validate_url(video_url):
            self.logger.error(f"Invalid URL: {video_url}")
            return None

        download_options = options or self.default_options

        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, self._download_audio_sync, video_url, download_options
            )
        except Exception as e:
            self.logger.error(f"Error downloading audio from {video_url}: {str(e)}")
            return None

    async def get_audio_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Obtiene información del audio sin descargarlo"""
        if not await self.validate_url(video_url):
            self.logger.error(f"Invalid URL for info extraction: {video_url}")
            return None

        try:
            opts = self._base_ydl_opts.copy()
            opts["extract_flat"] = True

            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None, self._get_audio_info_sync, video_url, opts
            )
        except Exception as e:
            self.logger.error(f"Error getting audio info from {video_url}: {str(e)}")
            return None

    async def validate_url(self, video_url: str) -> bool:
        """Valida si la URL es válida para descarga"""
        try:
            # Validaciones básicas
            if not video_url or not isinstance(video_url, str):
                return False

            # Validar que sea una URL de YouTube válida
            youtube_patterns = [
                r"^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+",
                r"^https?://(?:www\.)?youtu\.be/[\w-]+",
                r"^https?://(?:www\.)?youtube\.com/embed/[\w-]+",
            ]

            import re

            for pattern in youtube_patterns:
                if re.match(pattern, video_url):
                    return True

            self.logger.warning(f"URL does not match YouTube patterns: {video_url}")
            return False

        except Exception as e:
            self.logger.error(f"Error validating URL {video_url}: {str(e)}")
            return False

    def _download_audio_sync(
        self, video_url: str, options: DownloadOptions
    ) -> Optional[bytes]:
        """Descarga sincrónica del audio"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                output_path = f"{temp_dir}/{uuid.uuid4()}.%(ext)s"

                # Configurar opciones de yt-dlp
                ydl_opts = self._build_ydl_options(options, output_path)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    self.logger.debug(f"Starting download for: {video_url}")
                    ydl.download([video_url])

                # Buscar el archivo descargado
                audio_file = self._find_downloaded_file(temp_dir)
                if audio_file:
                    with open(audio_file, "rb") as f:
                        audio_data = f.read()

                    self.logger.info(
                        f"Successfully downloaded audio: {len(audio_data)} bytes"
                    )
                    return audio_data

                self.logger.warning(f"No audio file found after download: {video_url}")
                return None

            except Exception as e:
                self.logger.error(f"yt-dlp download error: {str(e)}")
                return None

    def _get_audio_info_sync(
        self, video_url: str, opts: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Obtiene información sincrónica del audio"""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                return {
                    "title": info.get("title", ""),
                    "duration": info.get("duration", 0),
                    "uploader": info.get("uploader", ""),
                    "formats": self._extract_audio_formats(info.get("formats", [])),
                    "filesize": info.get("filesize", 0),
                    "availability": info.get("availability", "unknown"),
                }
        except Exception as e:
            self.logger.error(f"yt-dlp info extraction error: {str(e)}")
            return None

    def _build_ydl_options(
        self, options: DownloadOptions, output_path: str
    ) -> Dict[str, Any]:
        """Construye las opciones para yt-dlp"""
        ydl_opts = self._base_ydl_opts.copy()

        ydl_opts.update(
            {
                "format": options.format,
                "extractaudio": options.extract_audio,
                "audioformat": options.audio_format,
                "audioquality": options.audio_quality,
                "quiet": options.quiet,
                "no_warnings": options.no_warnings,
                "outtmpl": output_path,
            }
        )

        return ydl_opts

    def _find_downloaded_file(self, temp_dir: str) -> Optional[str]:
        """Busca el archivo de audio descargado en el directorio temporal"""
        try:
            audio_extensions = [".mp3", ".m4a", ".webm", ".ogg", ".wav"]

            for file in os.listdir(temp_dir):
                if any(file.lower().endswith(ext) for ext in audio_extensions):
                    return os.path.join(temp_dir, file)

            return None

        except Exception as e:
            self.logger.error(f"Error finding downloaded file: {str(e)}")
            return None

    def _extract_audio_formats(self, formats: list) -> list:
        """Extrae información relevante de los formatos de audio"""
        audio_formats = []

        for fmt in formats:
            if fmt.get("acodec") != "none":  # Tiene audio
                audio_formats.append(
                    {
                        "format_id": fmt.get("format_id"),
                        "ext": fmt.get("ext"),
                        "acodec": fmt.get("acodec"),
                        "abr": fmt.get("abr"),  # Audio bitrate
                        "filesize": fmt.get("filesize"),
                        "quality": fmt.get("quality"),
                    }
                )

        return audio_formats
