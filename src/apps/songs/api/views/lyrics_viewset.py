from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.songs.use_cases.lyrics import GetSongLyricsUseCase
from common.utils.logging_config import get_logger

from ...infrastructure.repository.song_repository import SongRepository

logger = get_logger(__name__)


class LyricsView(APIView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.song_repository = SongRepository()
        self.get_lyrics_use_case = GetSongLyricsUseCase(self.song_repository)

    @extend_schema(
        tags=["Songs"],
        description="Get lyrics for a specific song. If lyrics don't exist, automatically searches for them.",
        request=None,
        summary="Get song lyrics",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "lyrics": {"type": "string", "nullable": True},
                },
            },
            404: {"description": "Song not found"},
        },
    )
    def get(self, request, song_id):
        lyrics = async_to_sync(self.get_lyrics_use_case.execute)(song_id)
        return Response({"lyrics": lyrics}, status=status.HTTP_200_OK)
