import asyncio

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins.logging_mixin import LoggingMixin

from ..infrastructure.repository.song_repository import SongRepository
from ..use_cases import (
    GetRandomSongsUseCase,
    GetSongByIdUseCase,
    IncrementPlayCountUseCase,
    SaveTrackAsSongUseCase,
    SearchSongsUseCase,
)
from .dtos import RandomSongsRequestDTO, SongSearchRequestDTO
from .mappers import SongMapper
from .serializers.song_serializers import (
    ProcessVideoRequestSerializer,
    SongListSerializer,
    SongSerializer,
)


class RandomSongsView(APIView, LoggingMixin):
    """Vista para obtener canciones aleatorias"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        # Import MusicService at class level to avoid circular imports
        from ...music_search.infrastructure.music_service import MusicService

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


class SearchSongsView(APIView, LoggingMixin):
    """Vista para buscar canciones"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        # Import MusicService at class level to avoid circular imports
        from ...music_search.infrastructure.music_service import MusicService

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


class ProcessYouTubeVideoView(APIView, LoggingMixin):
    """Vista para procesar un video específico de YouTube"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        # Import MusicService at class level to avoid circular imports
        from ...music_search.infrastructure.music_service import MusicService

        self.music_service = MusicService()
        self.save_track_use_case = SaveTrackAsSongUseCase(
            self.repository, self.music_service
        )
        self.mapper = SongMapper()

    @extend_schema(
        request=ProcessVideoRequestSerializer,
        responses={201: SongSerializer, 200: SongSerializer},
    )
    def post(self, request):
        """Procesa un video de YouTube y lo guarda como canción"""
        try:
            serializer = ProcessVideoRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            video_id = serializer.validated_data["video_id"]

            song = asyncio.run(self.save_track_use_case.execute({"video_id": video_id}))

            if not song:
                return Response(
                    {"error": "Failed to process YouTube video"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            song_dto = self.mapper.entity_to_response_dto(song)
            response_serializer = SongSerializer(song_dto)

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.logger.error(f"Error processing YouTube video: {str(e)}")
            return Response(
                {"error": "Failed to process video"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@api_view(["POST"])
def increment_play_count(request, song_id):
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
