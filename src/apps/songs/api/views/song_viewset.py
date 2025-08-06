from typing import Any

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import asyncio

from apps.songs.api.dtos import SongSearchRequestDTO
from apps.songs.api.mappers import SongMapper
from apps.songs.api.serializers.song_serializers import SongSerializer
from apps.songs.infrastructure.filters import SongModelFilter
from apps.songs.infrastructure.models import SongModel
from apps.songs.infrastructure.repository.song_repository import SongRepository
from apps.songs.use_cases import SearchSongsUseCase
from apps.songs.use_cases.lyrics_use_cases import GetSongLyricsUseCase, UpdateSongLyricsUseCase
from common.factories.unified_music_service_factory import get_music_service
from common.mixins import LoggingMixin


@extend_schema_view(
    list=extend_schema(
        tags=["Songs"],
        description="""
        List all songs with optional filtering.

        **Available Filters:**
        - `title`: Search by title (contains) - triggers YouTube search if enabled
        - `artist_name`: Search by artist name (contains)
        - `artist_id`: Filter by specific artist ID
        - `album_title`: Search by album title (contains)
        - `album_id`: Filter by specific album ID
        - `genre_name`: Search by genre (contains)
        - `source_type`: Source type (youtube, upload, spotify, etc.)
        - `audio_quality`: Audio quality (standard, high, lossless)
        - `min_duration`/`max_duration`: Duration range in seconds
        - `duration_range`: Predefined range (short|medium|long)
        - `min_play_count`/`max_play_count`: Play count range
        - `min_favorite_count`/`max_favorite_count`: Favorite count range
        - `min_download_count`/`max_download_count`: Download count range
        - `has_lyrics`: Only songs with lyrics
        - `has_file_url`: Only songs with audio file
        - `has_thumbnail`: Only songs with thumbnail
        - `created_after`/`created_before`: Creation date range
        - `last_played_after`/`last_played_before`: Last played date range
        - `release_after`/`release_before`: Release date range
        - `popular`: Only popular songs (>1000 plays)
        - `recent`: Only recently added songs
        - `trending`: Only trending songs (played recently)
        - `search`: General search in title, artist, album, and lyrics
        - `include_youtube`: Include YouTube results when using title search (default: true)
        - `min_results`: Minimum number of results to return (triggers YouTube search if needed)

        **Ordering:**
        Use `ordering` parameter with: title, duration_seconds, play_count,
        favorite_count, download_count, created_at, updated_at, last_played_at,
        release_date, artist__name, album__title, artist__followers_count

        **YouTube Integration:**
        When using the `title` parameter, if local results are fewer than
        `min_results` (default: 10) and `include_youtube` is true, the system
        will automatically search YouTube to complete the results.
        """,
        summary="Get songs list",
    ),
    retrieve=extend_schema(
        tags=["Songs"],
        description="Get a specific song by ID",
        summary="Get song details",
    ),
)
class SongViewSet(LoggingMixin, viewsets.ReadOnlyModelViewSet):
    """ViewSet para gestión de canciones (solo lectura) con filtros integrados y búsqueda en YouTube"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = SongRepository()
        self.music_service = get_music_service()
        self.search_songs_use_case = SearchSongsUseCase(
            self.repository, self.music_service
        )
        self.mapper = SongMapper()
        self.get_lyrics_use_case = GetSongLyricsUseCase()
        self.update_lyrics_use_case = UpdateSongLyricsUseCase()

    queryset = (
        SongModel.objects.select_related("artist", "album")
        .prefetch_related("genres")
        .all()
        .order_by("-created_at")
    )
    filterset_class = SongModelFilter
    permission_classes = [AllowAny]
    lookup_field = "id"
    lookup_url_kwarg = "id"

    # Campos por los que se puede ordenar
    ordering_fields = [
        "title",
        "duration_seconds",
        "play_count",
        "favorite_count",
        "download_count",
        "created_at",
        "updated_at",
        "last_played_at",
        "release_date",
        "artist__name",
        "album__title",
        "artist__followers_count",
    ]
    ordering = ["-created_at"]  # Ordenamiento por defecto

    # Búsqueda simple

    def get_serializer_class(self) -> Any:
        """
        Retorna el serializer para este ViewSet
        """
        return SongSerializer

    def get_queryset(self):
        """
        Personalizar el queryset base con optimizaciones y búsqueda en YouTube si es necesario
        """
        queryset = super().get_queryset()
        self.logger.info("Fetching songs with filters and optimizations")

        # Optimizar consultas incluyendo datos relacionados
        queryset = queryset.select_related("artist", "album").prefetch_related("genres")

        # Verificar si se está usando búsqueda por título
        title_query = (
            self.request.GET.get("title") if hasattr(self, "request") else None
        )

        if title_query:
            self.logger.info(f"Searching songs by title: {title_query}")
            # Aplicar filtros primero para obtener resultados locales
            filtered_queryset = self.filter_queryset(queryset)
            local_count = filtered_queryset.count()
            self.logger.info(
                f"Found {local_count} local results for title: {title_query}"
            )

            # Verificar parámetros de YouTube
            include_youtube = (
                self.request.GET.get("include_youtube", "true").lower() == "true"
            )
            min_results = int(self.request.GET.get("min_results", "10"))

            # Si hay pocos resultados locales y YouTube está habilitado
            if local_count < min_results and include_youtube:
                try:
                    self.logger.info(
                        f"Local results ({local_count}) < min_results ({min_results}), searching YouTube"
                    )
                    self._fetch_youtube_results(title_query, min_results - local_count)
                    # Refrescar queryset después de agregar nuevas canciones
                    queryset = (
                        super()
                        .get_queryset()
                        .select_related("artist", "album")
                        .prefetch_related("genres")
                    )
                    self.logger.info("Refreshed queryset after YouTube search")
                except Exception as e:
                    self.logger.error(f"Error fetching YouTube results: {str(e)}")
            else:
                self.logger.info(
                    f"Skipping YouTube search - local_count: {local_count}, min_results: {min_results}, include_youtube: {include_youtube}"
                )

        return queryset

    def _fetch_youtube_results(self, query: str, needed_count: int):
        """
        Busca canciones en YouTube y las guarda en la BD si no existen
        """
        try:
            self.logger.info(
                f"Fetching {needed_count} additional results from YouTube for title: '{query}'"
            )

            # Crear DTO para el caso de uso
            request_dto = SongSearchRequestDTO(
                query=query, limit=needed_count, include_youtube=True
            )

            self.logger.info(
                f"Created search DTO: query='{query}', limit={needed_count}, include_youtube=True"
            )

            # Ejecutar búsqueda usando el caso de uso existente (sin asyncio)
            self.logger.info("Starting YouTube search execution...")
            songs = self.search_songs_use_case.execute(request_dto)
            self.logger.info(
                f"Successfully fetched {len(songs)} songs from YouTube for title: '{query}'"
            )

            # Log some details about the songs found
            if songs:
                for i, song in enumerate(songs[:3]):  # Log first 3 songs
                    self.logger.info(f"Song {i+1}: {song.title} by {song.artist_name}")

        except Exception as e:
            self.logger.error(
                f"Error in _fetch_youtube_results for title '{query}': {str(e)}"
            )

    @extend_schema(
        tags=["Songs"],
        description="Get lyrics for a specific song. If lyrics don't exist, automatically searches for them.",
        summary="Get song lyrics",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "song_id": {"type": "string"},
                    "title": {"type": "string"},
                    "artist": {"type": "string"},
                    "lyrics": {"type": "string", "nullable": True},
                    "has_lyrics": {"type": "boolean"},
                    "source": {"type": "string", "description": "Source where lyrics were found"}
                }
            },
            404: {"description": "Song not found"}
        }
    )
    @action(detail=True, methods=['get'], url_path='lyrics')
    def get_lyrics(self, request, id=None):
        """Obtiene las letras de una canción específica"""
        try:
            fetch_if_missing = request.query_params.get('fetch_if_missing', 'true').lower() == 'true'
            
            # Ejecutar use case de forma asíncrona
            lyrics = asyncio.run(self.get_lyrics_use_case.execute(id, fetch_if_missing))
            
            # Obtener información de la canción
            try:
                song = SongModel.objects.select_related('artist').get(id=id)
                
                response_data = {
                    'song_id': str(song.id),
                    'title': song.title,
                    'artist': song.artist.name if song.artist else 'Unknown Artist',
                    'lyrics': lyrics,
                    'has_lyrics': lyrics is not None,
                    'source': 'database' if song.lyrics else ('external' if lyrics else None)
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
            except SongModel.DoesNotExist:
                return Response(
                    {'error': 'Song not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            self.logger.error(f"Error getting lyrics for song {id}: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        tags=["Songs"],
        description="Force update lyrics for a specific song, even if they already exist.",
        summary="Update song lyrics",
        responses={
            200: {
                "type": "object", 
                "properties": {
                    "song_id": {"type": "string"},
                    "title": {"type": "string"},
                    "artist": {"type": "string"},
                    "updated": {"type": "boolean"},
                    "lyrics": {"type": "string", "nullable": True},
                    "message": {"type": "string"}
                }
            },
            404: {"description": "Song not found"}
        }
    )
    @action(detail=True, methods=['post'], url_path='lyrics/update')
    def update_lyrics(self, request, id=None):
        """Actualiza las letras de una canción específica"""
        try:
            force_update = request.data.get('force_update', False)
            
            # Ejecutar use case de forma asíncrona
            updated = asyncio.run(self.update_lyrics_use_case.execute(id, force_update))
            
            # Obtener información actualizada de la canción
            try:
                song = SongModel.objects.select_related('artist').get(id=id)
                
                response_data = {
                    'song_id': str(song.id),
                    'title': song.title,
                    'artist': song.artist.name if song.artist else 'Unknown Artist',
                    'updated': updated,
                    'lyrics': song.lyrics,
                    'message': 'Lyrics updated successfully' if updated else 'No lyrics found or already exists'
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
                
            except SongModel.DoesNotExist:
                return Response(
                    {'error': 'Song not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            self.logger.error(f"Error updating lyrics for song {id}: {str(e)}")
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
