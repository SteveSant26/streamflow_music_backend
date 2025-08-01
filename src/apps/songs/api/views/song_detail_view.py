from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins.logging_mixin import LoggingMixin

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import GetSongByIdUseCase
from ..mappers import SongMapper
from ..serializers.song_serializers import SongSerializer


class SongDetailView(APIView, LoggingMixin):
    """Vista para detalles de una canción específica"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.get_song_by_id_use_case = GetSongByIdUseCase(self.repository)
        self.mapper = SongMapper()

    @extend_schema(responses={200: SongSerializer})
    def get(self, request, song_id):
        """Obtiene detalles de una canción"""
        try:
            song = self.get_song_by_id_use_case.execute(song_id)

            if not song:
                return Response(
                    {"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND
                )

            song_dto = self.mapper.entity_to_response_dto(song)
            serializer = SongSerializer(song_dto)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error getting song {song_id}: {str(e)}")
            return Response(
                {"error": "Failed to retrieve song"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
