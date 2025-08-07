from django.db.models import Q
from django_filters import rest_framework as filters

from apps.artists.infrastructure.models.artist_model import ArtistModel


class ArtistModelFilter(filters.FilterSet):
    """Filtros para el modelo ArtistModel"""

    # Filtros básicos
    name = filters.CharFilter(lookup_expr="icontains")

    # Filtros por seguidores
    min_followers_count = filters.NumberFilter(
        field_name="followers_count", lookup_expr="gte"
    )
    max_followers_count = filters.NumberFilter(
        field_name="followers_count", lookup_expr="lte"
    )

    # Filtros booleanos
    is_verified = filters.BooleanFilter()
    has_biography = filters.BooleanFilter(
        field_name="biography", lookup_expr="isnull", exclude=True
    )
    has_image = filters.BooleanFilter(
        field_name="image_url", lookup_expr="isnull", exclude=True
    )

    # Filtros por fechas
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    # Filtros especiales
    popular = filters.BooleanFilter(
        method="filter_popular", help_text="Filter popular artists (high followers)"
    )
    verified = filters.BooleanFilter(
        method="filter_verified", help_text="Filter only verified artists"
    )
    recent = filters.BooleanFilter(
        method="filter_recent", help_text="Filter recently added artists"
    )

    # Búsqueda general
    search = filters.CharFilter(
        method="filter_search", help_text="Search in name, biography, and country"
    )

    class Meta:
        model = ArtistModel
        fields = [
            "name",
            "is_verified",
            "min_followers_count",
            "max_followers_count",
            "has_biography",
            "has_image",
            "created_after",
            "created_before",
        ]

    def filter_popular(self, queryset, name, value):
        """Filtrar artistas populares (con muchos seguidores)"""
        if value:
            # Considerar populares a aquellos con más de 1000 seguidores
            return queryset.filter(followers_count__gte=1000).order_by(
                "-followers_count"
            )
        return queryset

    def filter_verified(self, queryset, name, value):
        """Filtrar solo artistas verificados"""
        if value:
            return queryset.filter(is_verified=True)
        return queryset

    def filter_recent(self, queryset, name, value):
        """Filtrar artistas agregados recientemente (últimos 30 días)"""
        if value:
            from datetime import timedelta

            from django.utils import timezone

            thirty_days_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=thirty_days_ago).order_by(
                "-created_at"
            )
        return queryset

    def filter_search(self, queryset, name, value):
        """Búsqueda general en nombre, biografía y país"""
        if value:
            return queryset.filter(
                Q(name__icontains=value) | Q(biography__icontains=value)
            )
        return queryset
