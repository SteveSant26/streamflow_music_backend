from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.albums.api.serializers import AlbumResponseSerializer
from apps.albums.infrastructure.filters import AlbumModelFilter
from apps.albums.infrastructure.models.album_model import AlbumModel
from common.mixins import FilteredViewSetMixin


@extend_schema_view(
    list=extend_schema(
        tags=["Albums"],
        description="""
        List all albums with optional filtering.

        **Available Filters:**
        - `title`: Search by title (contains)
        - `artist_name`: Search by artist name (contains)
        - `artist_id`: Filter by specific artist ID
        - `source_type`: Source type (manual, youtube, spotify, etc.)
        - `min_release_date`/`max_release_date`: Release date range
        - `release_year`: Specific release year
        - `min_total_tracks`/`max_total_tracks`: Track count range
        - `min_play_count`/`max_play_count`: Play count range
        - `has_cover_image`: Only albums with cover image
        - `has_description`: Only albums with description
        - `created_after`/`created_before`: Creation date range
        - `popular`: Only popular albums (>1000 plays)
        - `recent`: Only recently added albums
        - `search`: General search in title, artist, and description

        **Ordering:**
        Use `ordering` parameter with: title, release_date, total_tracks, play_count,
        created_at, updated_at, artist__name, artist__followers_count
        """,
        summary="Get albums list",
    ),
    retrieve=extend_schema(
        tags=["Albums"],
        description="Get a specific album by ID",
        summary="Get album details",
    ),
)
class AlbumViewSet(FilteredViewSetMixin):
    """ViewSet para gestión de álbumes (solo lectura) con filtros integrados"""

    queryset = AlbumModel.objects.select_related("artist").all().order_by("-created_at")
    filterset_class = AlbumModelFilter

    def get_serializer_class(self):
        return AlbumResponseSerializer

    # Campos por los que se puede ordenar
    ordering_fields = [
        "title",
        "release_date",
        "total_tracks",
        "play_count",
        "created_at",
        "updated_at",
        "artist__name",
        "artist__followers_count",
    ]
    ordering = ["-created_at"]

    # Búsqueda simple
    search_fields = ["title", "description", "artist__name"]

    def get_queryset(self):
        """
        Personalizar el queryset base con optimizaciones
        """
        queryset = super().get_queryset()

        # Optimizar consultas incluyendo datos relacionados
        queryset = queryset.select_related("artist")

        return queryset
