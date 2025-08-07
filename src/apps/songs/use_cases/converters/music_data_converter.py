"""
Conversor para transformar tipos de datos de música
"""

from typing import Union

from common.types.media_types import AudioTrackData, MusicTrackData


class MusicDataConverter:
    """Conversor para tipos de datos de música"""

    @staticmethod
    def convert_to_music_track_data(
        track: Union[MusicTrackData, AudioTrackData],
    ) -> MusicTrackData:
        """
        Convierte AudioTrackData a MusicTrackData si es necesario

        Args:
            track: Track data (MusicTrackData o AudioTrackData)

        Returns:
            MusicTrackData
        """
        # Si ya es MusicTrackData, retornarlo tal como está
        if isinstance(track, MusicTrackData):
            return track

        # Si es AudioTrackData, convertirlo a MusicTrackData
        return MusicTrackData(
            video_id=track.video_id,
            title=track.title,
            artist_name=track.artist_name,
            album_title=track.album_title,
            duration_seconds=track.duration_seconds,
            thumbnail_url=track.thumbnail_url,
            genre=track.genre,
            tags=track.tags,
            url=track.url,
            audio_file_data=track.audio_file_data,
            audio_file_name=track.audio_file_name,
        )
