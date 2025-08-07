from django.db.models import Q
from django_filters import rest_framework as filters

from apps.albums.infrastructure.models.album_model import AlbumModel


class AlbumModelFilter(filters.FilterSet):
    """Filtros para el modelo AlbumModel"""

    # Filtros básicos
    title = filters.CharFilter(lookup_expr="icontains")
    artist_name = filters.CharFilter(field_name="artist__name", lookup_expr="icontains")
    artist_id = filters.UUIDFilter(field_name="artist__id")

    # Filtros por fechas de lanzamiento
    min_release_date = filters.DateFilter(field_name="release_date", lookup_expr="gte")
    max_release_date = filters.DateFilter(field_name="release_date", lookup_expr="lte")
    release_year = filters.NumberFilter(method="filter_release_year")

    # Filtros por número de pistas
    min_total_tracks = filters.NumberFilter(
        field_name="total_tracks", lookup_expr="gte"
    )
    max_total_tracks = filters.NumberFilter(
        field_name="total_tracks", lookup_expr="lte"
    )

    # Filtros por reproducciones
    min_play_count = filters.NumberFilter(field_name="play_count", lookup_expr="gte")
    max_play_count = filters.NumberFilter(field_name="play_count", lookup_expr="lte")

    # Filtros booleanos
    has_cover_image = filters.BooleanFilter(
        field_name="cover_image_url", lookup_expr="isnull", exclude=True
    )
    has_description = filters.BooleanFilter(
        field_name="description", lookup_expr="isnull", exclude=True
    )

    # Filtros por fechas de creación
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    # Filtros especiales
    popular = filters.BooleanFilter(
        method="filter_popular", help_text="Filter popular albums (high play count)"
    )
    recent = filters.BooleanFilter(
        method="filter_recent", help_text="Filter recently added albums"
    )

    # Búsqueda general
    search = filters.CharFilter(
        method="filter_search",
        help_text="Search in title, artist name, and description",
    )

    class Meta:
        model = AlbumModel
        fields = [
            "title",
            "artist_name",
            "artist_id",
            "source_type",
            "min_release_date",
            "max_release_date",
            "release_year",
            "min_total_tracks",
            "max_total_tracks",
            "min_play_count",
            "max_play_count",
            "has_cover_image",
            "has_description",
            "created_after",
            "created_before",
            "popular",
            "recent",
            "search",
        ]

    def filter_release_year(self, queryset, name, value):
        """Filtrar álbumes por año de lanzamiento"""
        if value:
            return queryset.filter(release_date__year=value)
        return queryset

    def filter_popular(self, queryset, name, value):
        """Filtrar álbumes populares (con muchas reproducciones)"""
        if value:
            # Considerar populares a aquellos con más de 1000 reproducciones
            return queryset.filter(play_count__gte=1000).order_by("-play_count")
        return queryset

    def filter_recent(self, queryset, name, value):
        """Filtrar álbumes agregados recientemente (últimos 30 días)"""
        if value:
            from datetime import timedelta

            from django.utils import timezone

            thirty_days_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=thirty_days_ago).order_by(
                "-created_at"
            )
        return queryset

    def filter_search(self, queryset, name, value):
        """Búsqueda general en título, nombre del artista y descripción"""
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(artist__name__icontains=value)
                | Q(description__icontains=value)
            )
        return queryset
