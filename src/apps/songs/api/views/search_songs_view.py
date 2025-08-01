import asyncio

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins.logging_mixin import LoggingMixin

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import SearchSongsUseCase
from ..dtos import SongSearchRequestDTO
from ..mappers import SongMapper
from ..serializers.song_serializers import SongListSerializer


class SearchSongsView(APIView, LoggingMixin):
    """Vista para buscar canciones"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        # Import MusicService at class level to avoid circular imports
        from ....music_search.infrastructure.music_service import MusicService

        self.music_service = MusicService()
        self.search_songs_use_case = SearchSongsUseCase(
            self.repository, self.music_service
        )
        self.mapper = SongMapper()

    @extend_schema(
        responses={200: SongListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                "q", OpenApiTypes.STR, description="Search query", required=True
            ),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Number of results"
            ),
            OpenApiParameter(
                "include_youtube",
                OpenApiTypes.BOOL,
                description="Include YouTube search",
            ),
        ],
    )
    def get(self, request):
        """Busca canciones"""
        try:
            query = request.GET.get("q")
            if not query:
                return Response(
                    {"error": "Query parameter 'q' is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            limit = int(request.GET.get("limit", 20))
            include_youtube = (
                request.GET.get("include_youtube", "true").lower() == "true"
            )

            request_dto = SongSearchRequestDTO(
                query=query, limit=limit, include_youtube=include_youtube
            )

            # Ejecutar función async en el evento loop
            songs = asyncio.run(self.search_songs_use_case.execute(request_dto))

            songs_dtos = [self.mapper.entity_to_response_dto(song) for song in songs]
            serializer = SongListSerializer(songs_dtos, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error searching songs: {str(e)}")
            return Response(
                {"error": "Failed to search songs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
