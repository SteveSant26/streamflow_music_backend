"""Vista API para incrementar contador de reproducciones de canciones"""

from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response

from common.mixins.use_case_api_view_mixin import UseCaseAPIViewMixin

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import IncrementPlayCountUseCase
from ..dtos import IncrementCountRequestDTO


class IncrementPlayCountAPIView(UseCaseAPIViewMixin):
    """Vista para incrementar el contador de reproducciones de una canción"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.increment_use_case = IncrementPlayCountUseCase(self.repository)

    @extend_schema(
        tags=["Songs"],
        description="Increment the play count of a specific song",
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
        },
    )
    def post(self, request, song_id):
        """Incrementa el contador de reproducciones"""

        def execute_use_case():
            request_dto = IncrementCountRequestDTO(song_id=song_id)
            return async_to_sync(self.increment_use_case.execute)(request_dto)

        song = self.handle_use_case_execution(execute_use_case)

        if not song:
            return Response(
                {"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"play_count": song.play_count}, status=status.HTTP_200_OK)
