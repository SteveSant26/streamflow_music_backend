from django_filters import rest_framework as filters

from apps.songs.infrastructure.models import SongModel


class SongModelFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr="icontains")
    artist_name = filters.CharFilter(field_name="artist__name", lookup_expr="icontains")
    album_title = filters.CharFilter(field_name="album__title", lookup_expr="icontains")
    genre_name = filters.CharFilter(field_name="genres__name", lookup_expr="icontains")
    min_duration = filters.NumberFilter(
        field_name="duration_seconds", lookup_expr="gte"
    )
    max_duration = filters.NumberFilter(
        field_name="duration_seconds", lookup_expr="lte"
    )
    min_play_count = filters.NumberFilter(field_name="play_count", lookup_expr="gte")
    max_play_count = filters.NumberFilter(field_name="play_count", lookup_expr="lte")

    class Meta:
        model = SongModel
        fields = [
            "title",
            "artist_name",
            "album_title",
            "genre_name",
            "min_duration",
            "max_duration",
            "min_play_count",
            "max_play_count",
        ]
