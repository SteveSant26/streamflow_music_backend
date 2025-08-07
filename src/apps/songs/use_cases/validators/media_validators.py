import logging
from typing import Optional

from common.types.media_types.audio_types import MusicTrackData


class MediaValidators:
    """Validadores para archivos multimedia y storage"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_audio_download(
        self, music_track: MusicTrackData, audio_bytes: Optional[bytes]
    ) -> bool:
        """Valida que se haya descargado el audio si es necesario"""
        print(f"Validating audio download for track: {music_track.title}")
        print(f"Audio bytes: {audio_bytes is not None}")
        print(f"Audio file name: {music_track.audio_file_name}")
        if not music_track.audio_file_name and music_track.video_id and not audio_bytes:
            self.logger.error(
                f"❌ Failed to download audio for track: {music_track.title}. "
                f"Track will not be saved to database without audio."
            )
            return False
        return True

    def validate_storage_upload(
        self,
        music_track: MusicTrackData,
        audio_bytes: Optional[bytes],
        audio_file_name: Optional[str],
    ) -> bool:
        """Valida que el audio se haya subido correctamente al storage"""
        if not audio_file_name and audio_bytes:
            self.logger.error(
                f"❌ Failed to upload audio file to storage for track: {music_track.title}. "
                f"Track will not be saved to database."
            )
            return False
        return True

    def validate_file_url(
        self,
        music_track: MusicTrackData,
        audio_bytes: Optional[bytes],
        file_url: Optional[str],
    ) -> bool:
        """Valida que la URL del archivo sea accesible"""
        if audio_bytes and not file_url:
            self.logger.error(
                f"❌ Failed to get audio file URL from storage for track: {music_track.title}. "
                f"Track will not be saved to database."
            )
            return False
        return True
