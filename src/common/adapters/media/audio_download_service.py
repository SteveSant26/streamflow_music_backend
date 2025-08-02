import asyncio
import os
import tempfile
import uuid
from typing import Any, Dict, Optional

import yt_dlp

from src.config.music_service_config import get_optimized_ydl_options

from ...interfaces.imedia_service import IAudioDownloadService
from ...mixins.logging_mixin import LoggingMixin
from ...types.media_types import AudioServiceConfig, DownloadOptions
from ...utils.retry_manager import RetryManager
from ...utils.validators import MediaDataValidator, URLValidator
from ...utils.youtube_error_handler import YouTubeErrorHandler


class AudioDownloadService(IAudioDownloadService, LoggingMixin):
    """Servicio mejorado para descargar audio desde videos"""

    def __init__(
        self,
        config: Optional[AudioServiceConfig] = None,
        default_options: Optional[DownloadOptions] = None,
    ):
        super().__init__()
        self.config = config or AudioServiceConfig()
        self.default_options = default_options or DownloadOptions()

        # Componentes auxiliares
        self.url_validator = URLValidator()
        self.media_validator = MediaDataValidator()
        self.retry_manager = RetryManager(
            max_retries=self.config.max_retries, base_delay=self.config.retry_delay
        )
        self.error_handler = YouTubeErrorHandler()

        # Configuración base para yt-dlp
        self._base_ydl_opts = self._build_base_ydl_options()

    def _build_base_ydl_options(self) -> Dict[str, Any]:
        """Construye las opciones base optimizadas para yt-dlp"""
        # Usar configuraciones optimizadas
        base_options = get_optimized_ydl_options()

        # Agregar configuraciones específicas del servicio
        base_options.update(
            {
                "outtmpl": {"default": "%(id)s.%(ext)s"},
                "restrictfilenames": True,
                "windowsfilenames": True,
                "trim_filename": 100,
            }
        )

        return base_options

    async def download_audio(
        self, video_url: str, options: Optional[DownloadOptions] = None
    ) -> Optional[bytes]:
        """Descarga el audio de un video como bytes"""
        if not self.url_validator.validate_youtube_url(video_url):
            self.logger.error(f"Invalid URL: {video_url}")
            return None

        download_options = options or self.default_options

        try:
            return await self.retry_manager.execute_with_retry(
                self._download_audio_with_timeout, video_url, download_options
            )
        except Exception as e:
            self.logger.error(f"Error downloading audio from {video_url}: {str(e)}")
            return None

    async def _download_audio_with_timeout(
        self, video_url: str, options: DownloadOptions
    ) -> Optional[bytes]:
        """Descarga audio con timeout"""
        try:
            return await asyncio.wait_for(
                self._download_audio_internal(video_url, options),
                timeout=options.timeout,
            )
        except asyncio.TimeoutError:
            self.logger.error(f"Download timeout for {video_url}")
            return None

    async def _download_audio_internal(
        self, video_url: str, options: DownloadOptions
    ) -> Optional[bytes]:
        """Lógica interna de descarga"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._download_audio_sync, video_url, options
        )

    async def get_audio_info(self, video_url: str) -> Optional[Dict[str, Any]]:
        """Obtiene información del audio sin descargarlo"""
        if not self.url_validator.validate_youtube_url(video_url):
            self.logger.error(f"Invalid URL for info extraction: {video_url}")
            return None

        try:
            return await self.retry_manager.execute_with_retry(
                self._get_audio_info_with_timeout, video_url
            )
        except Exception as e:
            self.logger.error(f"Error getting audio info from {video_url}: {str(e)}")
            return None

    async def _get_audio_info_with_timeout(
        self, video_url: str
    ) -> Optional[Dict[str, Any]]:
        """Obtiene información con timeout"""
        try:
            return await asyncio.wait_for(
                self._get_audio_info_internal(video_url),
                timeout=self.config.request_timeout,
            )
        except asyncio.TimeoutError:
            self.logger.error(f"Info extraction timeout for {video_url}")
            return None

    async def _get_audio_info_internal(
        self, video_url: str
    ) -> Optional[Dict[str, Any]]:
        """Lógica interna para obtener información"""
        opts = self._base_ydl_opts.copy()
        opts["extract_flat"] = True

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._get_audio_info_sync, video_url, opts
        )

    async def validate_url(self, video_url: str) -> bool:
        """Valida si la URL es válida para descarga"""
        return self.url_validator.validate_youtube_url(video_url)

    def _download_audio_sync(
        self, video_url: str, options: DownloadOptions
    ) -> Optional[bytes]:
        """Descarga sincrónica del audio usando configuración simplificada como ApiEjemplo"""
        temp_dir = self.config.temp_dir or tempfile.gettempdir()

        with tempfile.TemporaryDirectory(dir=temp_dir) as working_dir:
            try:
                # Usar configuración simple similar a ApiEjemplo
                return self._simple_download_approach(video_url, options, working_dir)
            except Exception as e:
                self.logger.warning(f"Simple download failed: {str(e)}")

                # Solo intentar un método de fallback si el primero falla
                try:
                    return self._fallback_download_approach(
                        video_url, options, working_dir
                    )
                except Exception as fallback_error:
                    self.logger.error(
                        f"All download approaches failed: {str(fallback_error)}"
                    )
                    return None

    def _simple_download_approach(
        self, video_url: str, options: DownloadOptions, working_dir: str
    ) -> Optional[bytes]:
        """Enfoque simple de descarga basado en configuración probada exitosamente"""
        output_path = f"{working_dir}/{uuid.uuid4()}.%(ext)s"

        # Usar configuración optimizada que ya fue probada y funciona
        ydl_opts = get_optimized_ydl_options()
        ydl_opts["outtmpl"] = output_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self.logger.debug(f"Starting simple download for: {video_url}")
            ydl.download([video_url])

        # Buscar el archivo descargado
        audio_file = self._find_downloaded_file(working_dir)
        if audio_file:
            return self._read_and_validate_audio_file(audio_file, options)

        self.logger.warning(f"No audio file found after simple download: {video_url}")
        return None

    def _fallback_download_approach(
        self, video_url: str, options: DownloadOptions, working_dir: str
    ) -> Optional[bytes]:
        """Enfoque de fallback con configuración alternativa"""
        output_path = f"{working_dir}/{uuid.uuid4()}.%(ext)s"

        # Configuración alternativa más permisiva
        ydl_opts = self._build_ydl_options(options, output_path)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self.logger.debug(f"Starting fallback download for: {video_url}")
            ydl.download([video_url])

        # Buscar el archivo descargado
        audio_file = self._find_downloaded_file(working_dir)
        if audio_file:
            return self._read_and_validate_audio_file(audio_file, options)

        self.logger.warning(f"No audio file found after fallback download: {video_url}")
        return None

    def _attempt_download_with_config(
        self,
        video_url: str,
        options: DownloadOptions,
        working_dir: str,
        use_enhanced: bool = False,
        # fallback_config: Optional[Dict[str, Any]] = None,
    ) -> Optional[bytes]:
        """Método simplificado de descarga (mantenido por compatibilidad)"""
        # Delegar a los nuevos métodos simplificados
        if use_enhanced:
            return self._simple_download_approach(video_url, options, working_dir)
        else:
            return self._fallback_download_approach(video_url, options, working_dir)

    def _read_and_validate_audio_file(
        self, audio_file: str, options: DownloadOptions
    ) -> Optional[bytes]:
        """Lee y valida el archivo de audio descargado"""
        try:
            # Validar formato
            if not self.media_validator.validate_audio_format(audio_file):
                self.logger.warning(f"Invalid audio format: {audio_file}")
                return None

            # Validar tamaño
            file_size = os.path.getsize(audio_file)
            max_size = options.max_filesize or (100 * 1024 * 1024)  # 100MB default

            if not self.media_validator.validate_filesize(file_size, max_size):
                self.logger.warning(f"File too large: {file_size} bytes")
                return None

            # Leer archivo
            with open(audio_file, "rb") as f:
                audio_data = f.read()

            self.logger.info(f"Successfully downloaded audio: {len(audio_data)} bytes")
            return audio_data

        except Exception as e:
            self.logger.error(f"Error reading audio file {audio_file}: {str(e)}")
            return None

    def _get_audio_info_sync(
        self, video_url: str, opts: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Obtiene información sincrónica del audio"""
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    self.logger.error(f"No info extracted for URL: {video_url}")
                    return None

                return self._process_audio_info(info)

        except Exception as e:
            self.logger.error(f"yt-dlp info extraction error: {str(e)}")
            return None

    def _process_audio_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa y valida la información extraída"""
        duration = info.get("duration", 0)
        if not self.media_validator.validate_duration(duration):
            self.logger.warning(f"Invalid duration: {duration} seconds")

        return {
            "title": info.get("title", ""),
            "duration": duration,
            "uploader": info.get("uploader", ""),
            "formats": self._extract_audio_formats(info.get("formats", [])),
            "filesize": info.get("filesize", 0),
            "availability": info.get("availability", "unknown"),
            "view_count": info.get("view_count", 0),
            "like_count": info.get("like_count", 0),
        }

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
            for file in os.listdir(temp_dir):
                if self.media_validator.validate_audio_format(file):
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
