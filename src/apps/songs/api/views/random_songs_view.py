import asyncio

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins.logging_mixin import LoggingMixin

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import GetRandomSongsUseCase
from ..dtos import RandomSongsRequestDTO
from ..mappers import SongMapper
from ..serializers.song_serializers import SongListSerializer


@extend_schema_view(
    get=extend_schema(
        tags=["Songs"],
        description="Get random songs from the database with optional refresh from YouTube",
    )
)
class RandomSongsView(APIView, LoggingMixin):
    """Vista para obtener canciones aleatorias"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        # Import MusicService at class level to avoid circular imports
        from ....music_search.infrastructure.music_service import MusicService

        self.music_service = MusicService()
        self.get_random_songs_use_case = GetRandomSongsUseCase(
            self.repository, self.music_service
        )
        self.mapper = SongMapper()

    @extend_schema(
        responses={200: SongListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                "count", OpenApiTypes.INT, description="Number of songs to return"
            ),
            OpenApiParameter(
                "force_refresh",
                OpenApiTypes.BOOL,
                description="Force refresh from YouTube",
            ),
        ],
    )
    def get(self, request):
        """Obtiene canciones aleatorias"""
        try:
            count = int(request.GET.get("count", 6))
            force_refresh = request.GET.get("force_refresh", "false").lower() == "true"

            request_dto = RandomSongsRequestDTO(
                count=count, force_refresh=force_refresh
            )

            # Ejecutar función async en el evento loop
            songs = asyncio.run(self.get_random_songs_use_case.execute(request_dto))

            songs_dtos = [self.mapper.entity_to_response_dto(song) for song in songs]
            serializer = SongListSerializer(songs_dtos, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error getting random songs: {str(e)}")
            return Response(
                {"error": "Failed to retrieve random songs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
