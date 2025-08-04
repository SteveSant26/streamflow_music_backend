from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.artists.api.serializers import ArtistResponseSerializer
from apps.artists.infrastructure.filters import ArtistModelFilter
from apps.artists.infrastructure.models import ArtistModel
from common.mixins import FilteredViewSetMixin


@extend_schema_view(
    list=extend_schema(
        tags=["Artists"],
        description="""
        List all artists with optional filtering.

        **Available Filters:**
        - `name`: Search by name (contains)
        - `country`: Filter by exact country
        - `is_verified`: Only verified artists
        - `min_followers_count`/`max_followers_count`: Followers count range
        - `popular`: Only popular artists (>1000 followers)
        - `verified`: Only verified artists
        - `recent`: Only recently added artists
        - `search`: General search in name, biography, and country
        - `has_biography`: Only artists with biography
        - `has_image`: Only artists with image
        - `created_after`/`created_before`: Creation date range
        - `source_type`: Source type (manual, youtube, spotify, etc.)

        **Ordering:**
        Use `ordering` parameter with: name, followers_count, created_at, updated_at
        """,
        summary="Get artists list",
    ),
    retrieve=extend_schema(
        tags=["Artists"],
        description="Get a specific artist by ID",
        summary="Get artist details",
    ),
)
class ArtistViewSet(FilteredViewSetMixin):
    """ViewSet para gestión de artistas (solo lectura) con filtros integrados"""

    queryset = ArtistModel.objects.all().order_by("-created_at")
    serializer_class = ArtistResponseSerializer
    filterset_class = ArtistModelFilter

    # Campos por los que se puede ordenar
    ordering_fields = ["name", "followers_count", "created_at", "updated_at"]
    ordering = ["-created_at"]  # Ordenamiento por defecto

    # Búsqueda simple
    search_fields = ["name", "biography", "country"]
