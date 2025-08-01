from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import IncrementPlayCountUseCase


@api_view(["POST"])
def increment_play_count_view(request, song_id):
    """Incrementa el contador de reproducciones"""
    try:
        repository = SongRepository()
        increment_use_case = IncrementPlayCountUseCase(repository)

        song = increment_use_case.execute(song_id)

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
