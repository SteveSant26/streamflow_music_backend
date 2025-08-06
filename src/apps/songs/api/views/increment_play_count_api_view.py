"""Vista API para incrementar contador de reproducciones de canciones"""

from asgiref.sync import async_to_sync
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import IncrementPlayCountUseCase
from ..dtos import IncrementCountRequestDTO


class IncrementPlayCountAPIView(APIView):
    """Vista para incrementar el contador de reproducciones de una canción"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.increment_use_case = IncrementPlayCountUseCase(self.repository)

    @extend_schema(
        tags=["Songs"],
        description="Increment the play count of a specific song",
        request=None,  # No request body needed for this endpoint
        parameters=[
            OpenApiParameter(
                name="song_id",
                location=OpenApiParameter.PATH,
                required=True,
                type=OpenApiTypes.UUID,
                description="The ID of the song to increment play count",
            )
        ],
        responses={
            200: {
                "type": "object",
                "properties": {
                    "play_count": {
                        "type": "integer",
                        "description": "Updated play count",
                    }
                },
            },
            404: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Song not found"}
                },
            },
            500: {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Internal server error"}
                },
            },
        },
    )
    def post(self, request, song_id):
        """Incrementa el contador de reproducciones"""
        try:
            request_dto = IncrementCountRequestDTO(song_id=song_id)
            song = async_to_sync(self.increment_use_case.execute)(request_dto)

            if not song:
                return Response(
                    {"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND
                )

            return Response({"play_count": song.play_count}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
