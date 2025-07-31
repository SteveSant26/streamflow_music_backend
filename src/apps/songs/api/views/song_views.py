import asyncio

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins.logging_mixin import LoggingMixin

from ...domain.entities import SongEntity
from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases.song_use_cases import SongUseCases
from ..serializers.song_serializers import (
    ProcessVideoRequestSerializer,
    SongListSerializer,
    SongSerializer,
)


def entity_to_dict(entity: SongEntity) -> dict:
    """Convierte una entidad a diccionario para el serializer"""
    return {
        "id": entity.id,
        "title": entity.title,
        "artist_name": entity.artist_name,
        "album_title": entity.album_title,
        "genre_name": entity.genre_name,
        "duration_seconds": entity.duration_seconds,
        "file_url": entity.file_url,
        "thumbnail_url": entity.thumbnail_url,
        "tags": entity.tags or [],
        "play_count": entity.play_count,
        "favorite_count": entity.favorite_count,
        "download_count": entity.download_count,
        "source_type": entity.source_type,
        "source_id": entity.source_id,
        "source_url": entity.source_url,
        "is_explicit": entity.is_explicit,
        "is_premium": entity.is_premium,
        "audio_quality": entity.audio_quality,
        "created_at": entity.created_at,
        "last_played_at": entity.last_played_at,
        "release_date": entity.release_date,
    }


class RandomSongsView(APIView, LoggingMixin):
    """Vista para obtener canciones aleatorias"""

    def __init__(self):
        super().__init__()
        self.song_use_cases = SongUseCases(SongRepository())

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

            # Ejecutar función async en el evento loop
            songs = asyncio.run(
                self.song_use_cases.get_random_songs(count, force_refresh)
            )

            songs_data = [entity_to_dict(song) for song in songs]
            serializer = SongListSerializer(songs_data, many=True)

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
        self.song_use_cases = SongUseCases(SongRepository())

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

            # Ejecutar función async en el evento loop
            songs = asyncio.run(
                self.song_use_cases.search_songs(query, limit, include_youtube)
            )

            songs_data = [entity_to_dict(song) for song in songs]
            serializer = SongListSerializer(songs_data, many=True)

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
        self.song_use_cases = SongUseCases(SongRepository())

    @extend_schema(responses={200: SongSerializer})
    def get(self, request, song_id):
        """Obtiene detalles de una canción"""
        try:
            song = asyncio.run(self.song_use_cases.get_song_by_id(song_id))

            if not song:
                return Response(
                    {"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND
                )

            song_data = entity_to_dict(song)
            serializer = SongSerializer(song_data)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error getting song {song_id}: {str(e)}")
            return Response(
                {"error": "Failed to retrieve song"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MostPlayedSongsView(APIView, LoggingMixin):
    """Vista para obtener las canciones más reproducidas"""

    def __init__(self):
        super().__init__()
        self.song_use_cases = SongUseCases(SongRepository())

    @extend_schema(
        responses={200: SongListSerializer(many=True)},
        parameters=[
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Number of songs to return"
            ),
        ],
    )
    def get(self, request):
        """Obtiene las canciones más reproducidas"""
        try:
            limit = int(request.GET.get("limit", 10))

            songs = asyncio.run(self.song_use_cases.get_most_played_songs(limit))

            songs_data = [entity_to_dict(song) for song in songs]
            serializer = SongListSerializer(songs_data, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error getting most played songs: {str(e)}")
            return Response(
                {"error": "Failed to retrieve most played songs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TrendingArtistsView(APIView, LoggingMixin):
    """Vista para obtener los artistas más populares"""

    def __init__(self):
        super().__init__()
        self.song_use_cases = SongUseCases(SongRepository())

    @extend_schema(
        responses={200: dict},
        parameters=[
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Number of artists to return"
            ),
        ],
    )
    def get(self, request):
        """Obtiene los artistas más populares"""
        try:
            limit = int(request.GET.get("limit", 10))

            artists = asyncio.run(self.song_use_cases.get_trending_artists(limit))

            return Response(artists, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error getting trending artists: {str(e)}")
            return Response(
                {"error": "Failed to retrieve trending artists"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TrendingAlbumsView(APIView, LoggingMixin):
    """Vista para obtener los álbumes más populares"""

    def __init__(self):
        super().__init__()
        self.song_use_cases = SongUseCases(SongRepository())

    @extend_schema(
        responses={200: dict},
        parameters=[
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Number of albums to return"
            ),
        ],
    )
    def get(self, request):
        """Obtiene los álbumes más populares"""
        try:
            limit = int(request.GET.get("limit", 10))

            albums = asyncio.run(self.song_use_cases.get_trending_albums(limit))

            return Response(albums, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error getting trending albums: {str(e)}")
            return Response(
                {"error": "Failed to retrieve trending albums"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ProcessYouTubeVideoView(APIView, LoggingMixin):
    """Vista para procesar un video específico de YouTube"""

    def __init__(self):
        super().__init__()
        self.song_use_cases = SongUseCases(SongRepository())

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

            song = asyncio.run(self.song_use_cases.process_youtube_video(video_id))

            if not song:
                return Response(
                    {"error": "Failed to process YouTube video"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            song_data = entity_to_dict(song)
            response_serializer = SongSerializer(song_data)

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
        song_use_cases = SongUseCases(SongRepository())
        song = asyncio.run(song_use_cases.increment_play_count(song_id))

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


@api_view(["POST"])
def increment_favorite_count(request, song_id):
    """Incrementa el contador de favoritos"""
    try:
        song_use_cases = SongUseCases(SongRepository())
        song = asyncio.run(song_use_cases.increment_favorite_count(song_id))

        if not song:
            return Response(
                {"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"favorite_count": song.favorite_count}, status=status.HTTP_200_OK
        )

    except Exception:
        return Response(
            {"error": "Failed to increment favorite count"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def increment_download_count(request, song_id):
    """Incrementa el contador de descargas"""
    try:
        song_use_cases = SongUseCases(SongRepository())
        song = asyncio.run(song_use_cases.increment_download_count(song_id))

        if not song:
            return Response(
                {"error": "Song not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"download_count": song.download_count}, status=status.HTTP_200_OK
        )

    except Exception:
        return Response(
            {"error": "Failed to increment download count"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
