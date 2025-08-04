from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from apps.songs.api.serializers.song_serializers import SongSerializer
from apps.songs.infrastructure.filters import SongModelFilter
from apps.songs.infrastructure.models import SongModel
from common.mixins.logging_mixin import LoggingMixin


@extend_schema_view(
    list=extend_schema(tags=["Songs"], description="List all songs with filtering"),
    retrieve=extend_schema(tags=["Songs"], description="Get a specific song"),
)
class SongViewSet(viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para gestión de canciones (solo lectura)"""

    queryset = (
        SongModel.objects.select_related("artist", "album")
        .prefetch_related("genres")
        .all()
    )
    serializer_class = SongSerializer
    permission_classes = [AllowAny]
    filterset_class = SongModelFilter

    def get_permissions(self):
        """Define permisos según la acción"""
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
