from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.songs.api.serializers.song_serializers import SongSerializer
from apps.songs.infrastructure.filters import SongModelFilter
from apps.songs.infrastructure.models import SongModel
from common.mixins import FilteredViewSetMixin


@extend_schema_view(
    list=extend_schema(
        tags=["Songs"],
        description="""
        List all songs with optional filtering.

        **Available Filters:**
        - `title`: Search by title (contains)
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

        **Ordering:**
        Use `ordering` parameter with: title, duration_seconds, play_count,
        favorite_count, download_count, created_at, updated_at, last_played_at,
        release_date, artist__name, album__title, artist__followers_count
        """,
        summary="Get songs list",
    ),
    retrieve=extend_schema(
        tags=["Songs"],
        description="Get a specific song by ID",
        summary="Get song details",
    ),
)
class SongViewSet(FilteredViewSetMixin):
    """ViewSet para gestión de canciones (solo lectura) con filtros integrados"""

    queryset = (
        SongModel.objects.select_related("artist", "album")
        .prefetch_related("genres")
        .all()
        .order_by("-created_at")
    )
    serializer_class = SongSerializer
    filterset_class = SongModelFilter
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
    search_fields = ["title", "lyrics", "artist__name", "album__title", "genres__name"]

    def get_queryset(self):
        """
        Personalizar el queryset base con optimizaciones
        """
        queryset = super().get_queryset()

        # Optimizar consultas incluyendo datos relacionados
        queryset = queryset.select_related("artist", "album").prefetch_related("genres")

        return queryset
