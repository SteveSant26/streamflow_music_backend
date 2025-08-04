from django.db.models import Q
from django_filters import rest_framework as filters

from apps.songs.infrastructure.models import SongModel


class SongModelFilter(filters.FilterSet):
    """Filtros para el modelo SongModel"""

    # Filtros básicos
    title = filters.CharFilter(lookup_expr="icontains")
    artist_name = filters.CharFilter(field_name="artist__name", lookup_expr="icontains")
    artist_id = filters.UUIDFilter(field_name="artist__id")
    album_title = filters.CharFilter(field_name="album__title", lookup_expr="icontains")
    album_id = filters.UUIDFilter(field_name="album__id")
    genre_name = filters.CharFilter(field_name="genres__name", lookup_expr="icontains")
    source_type = filters.ChoiceFilter(
        choices=SongModel._meta.get_field("source_type").choices
    )
    audio_quality = filters.ChoiceFilter(
        choices=SongModel._meta.get_field("audio_quality").choices
    )

    # Filtros por duración
    min_duration = filters.NumberFilter(
        field_name="duration_seconds", lookup_expr="gte"
    )
    max_duration = filters.NumberFilter(
        field_name="duration_seconds", lookup_expr="lte"
    )
    duration_range = filters.CharFilter(
        method="filter_duration_range", help_text="short|medium|long"
    )

    # Filtros por reproducciones
    min_play_count = filters.NumberFilter(field_name="play_count", lookup_expr="gte")
    max_play_count = filters.NumberFilter(field_name="play_count", lookup_expr="lte")

    # Filtros por favoritos y descargas
    min_favorite_count = filters.NumberFilter(
        field_name="favorite_count", lookup_expr="gte"
    )
    max_favorite_count = filters.NumberFilter(
        field_name="favorite_count", lookup_expr="lte"
    )
    min_download_count = filters.NumberFilter(
        field_name="download_count", lookup_expr="gte"
    )
    max_download_count = filters.NumberFilter(
        field_name="download_count", lookup_expr="lte"
    )

    # Filtros booleanos
    has_lyrics = filters.BooleanFilter(
        field_name="lyrics", lookup_expr="isnull", exclude=True
    )
    has_file_url = filters.BooleanFilter(
        field_name="file_url", lookup_expr="isnull", exclude=True
    )
    has_thumbnail = filters.BooleanFilter(
        field_name="thumbnail_url", lookup_expr="isnull", exclude=True
    )

    # Filtros por fechas
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
    last_played_after = filters.DateTimeFilter(
        field_name="last_played_at", lookup_expr="gte"
    )
    last_played_before = filters.DateTimeFilter(
        field_name="last_played_at", lookup_expr="lte"
    )
    release_after = filters.DateTimeFilter(field_name="release_date", lookup_expr="gte")
    release_before = filters.DateTimeFilter(
        field_name="release_date", lookup_expr="lte"
    )

    # Filtros especiales
    popular = filters.BooleanFilter(
        method="filter_popular", help_text="Filter popular songs (high play count)"
    )
    recent = filters.BooleanFilter(
        method="filter_recent", help_text="Filter recently added songs"
    )
    trending = filters.BooleanFilter(
        method="filter_trending", help_text="Filter trending songs (recently played)"
    )

    # Búsqueda general
    search = filters.CharFilter(
        method="filter_search", help_text="Search in title, artist, album, and lyrics"
    )

    class Meta:
        model = SongModel
        fields = [
            "title",
            "artist_name",
            "artist_id",
            "album_title",
            "album_id",
            "genre_name",
            "source_type",
            "audio_quality",
            "min_duration",
            "max_duration",
            "duration_range",
            "min_play_count",
            "max_play_count",
            "min_favorite_count",
            "max_favorite_count",
            "min_download_count",
            "max_download_count",
            "has_lyrics",
            "has_file_url",
            "has_thumbnail",
            "created_after",
            "created_before",
            "last_played_after",
            "last_played_before",
            "release_after",
            "release_before",
            "popular",
            "recent",
            "trending",
            "search",
        ]

    def filter_duration_range(self, queryset, name, value):
        """Filtrar canciones por rango de duración"""
        if value == "short":
            # Canciones cortas: menos de 3 minutos (180 segundos)
            return queryset.filter(duration_seconds__lt=180)
        elif value == "medium":
            # Canciones medianas: entre 3 y 6 minutos
            return queryset.filter(duration_seconds__gte=180, duration_seconds__lte=360)
        elif value == "long":
            # Canciones largas: más de 6 minutos
            return queryset.filter(duration_seconds__gt=360)
        return queryset

    def filter_popular(self, queryset, name, value):
        """Filtrar canciones populares (con muchas reproducciones)"""
        if value:
            # Considerar populares a aquellas con más de 1000 reproducciones
            return queryset.filter(play_count__gte=1000).order_by("-play_count")
        return queryset

    def filter_recent(self, queryset, name, value):
        """Filtrar canciones agregadas recientemente (últimos 30 días)"""
        if value:
            from datetime import timedelta

            from django.utils import timezone

            thirty_days_ago = timezone.now() - timedelta(days=30)
            return queryset.filter(created_at__gte=thirty_days_ago).order_by(
                "-created_at"
            )
        return queryset

    def filter_trending(self, queryset, name, value):
        """Filtrar canciones en tendencia (reproducidas recientemente)"""
        if value:
            from datetime import timedelta

            from django.utils import timezone

            seven_days_ago = timezone.now() - timedelta(days=7)
            return queryset.filter(last_played_at__gte=seven_days_ago).order_by(
                "-last_played_at", "-play_count"
            )
        return queryset

    def filter_search(self, queryset, name, value):
        """Búsqueda general en título, artista, álbum y letra"""
        if value:
            return queryset.filter(
                Q(title__icontains=value)
                | Q(artist__name__icontains=value)
                | Q(album__title__icontains=value)
                | Q(lyrics__icontains=value)
                | Q(genres__name__icontains=value)
            ).distinct()  # distinct() para evitar duplicados por joins
        return queryset
