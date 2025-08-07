# apps/playlists/infrastructure/filters.py

from django.db.models import Count
from django_filters import rest_framework as filters

from apps.playlists.infrastructure.models.playlist_model import PlaylistModel


class PlaylistModelFilter(filters.FilterSet):
    """Filtros para el modelo de Playlist"""

    name = filters.CharFilter(lookup_expr="icontains")
    description = filters.CharFilter(lookup_expr="icontains")
    is_public = filters.BooleanFilter()
    is_default = filters.BooleanFilter()
    user_id = filters.UUIDFilter(field_name="user__id")
    user_username = filters.CharFilter(
        field_name="user__username", lookup_expr="icontains"
    )
    has_description = filters.BooleanFilter(
        field_name="description", lookup_expr="isnull", exclude=True
    )
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    updated_after = filters.DateTimeFilter(field_name="updated_at", lookup_expr="gte")
    updated_before = filters.DateTimeFilter(field_name="updated_at", lookup_expr="lte")
    min_song_count = filters.NumberFilter(method="filter_min_song_count")
    max_song_count = filters.NumberFilter(method="filter_max_song_count")

    class Meta:
        model = PlaylistModel
        fields = [
            "name",
            "is_public",
            "is_default",
        ]

    def filter_min_song_count(self, queryset, name, value):
        """Filtra playlists con un mínimo número de canciones"""
        return queryset.annotate(song_count=Count("playlist_songs")).filter(
            song_count__gte=value
        )

    def filter_max_song_count(self, queryset, name, value):
        """Filtra playlists con un máximo número de canciones"""
        return queryset.annotate(song_count=Count("playlist_songs")).filter(
            song_count__lte=value
        )
