from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import IncrementPlayCountUseCase


@extend_schema(
    tags=["Songs"],
    description="Increment the play count of a specific song",
    responses={
        200: {
            "type": "object",
            "properties": {
                "play_count": {"type": "integer", "description": "Updated play count"}
            },
        },
        404: {
            "type": "object",
            "properties": {"error": {"type": "string", "example": "Song not found"}},
        },
        500: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Failed to increment play count"}
            },
        },
    },
)
@api_view(["POST"])
async def increment_play_count_view(request, song_id):
    """Incrementa el contador de reproducciones"""
    try:
        repository = SongRepository()
        increment_use_case = IncrementPlayCountUseCase(repository)

        song = await increment_use_case.execute(song_id)

        if not song:
            return Response(
                {"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"play_count": song.play_count}, status=status.HTTP_200_OK)

    except Exception:
        return Response(
            {"error": "Failed to increment play count"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
