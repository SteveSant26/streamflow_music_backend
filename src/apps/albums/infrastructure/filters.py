from django_filters import rest_framework as filters

from apps.albums.infrastructure.models.album_model import AlbumModel


class AlbumModelFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr="icontains")
    artist_name = filters.CharFilter(field_name="artist__name", lookup_expr="icontains")
    artist_id = filters.UUIDFilter(field_name="artist__id")
    min_release_date = filters.DateFilter(field_name="release_date", lookup_expr="gte")
    max_release_date = filters.DateFilter(field_name="release_date", lookup_expr="lte")
    min_total_tracks = filters.NumberFilter(
        field_name="total_tracks", lookup_expr="gte"
    )
    max_total_tracks = filters.NumberFilter(
        field_name="total_tracks", lookup_expr="lte"
    )
    min_play_count = filters.NumberFilter(field_name="play_count", lookup_expr="gte")
    max_play_count = filters.NumberFilter(field_name="play_count", lookup_expr="lte")
    source_type = filters.ChoiceFilter(
        choices=[
            ("manual", "Manual"),
            ("youtube", "YouTube"),
            ("spotify", "Spotify"),
            ("soundcloud", "SoundCloud"),
        ]
    )
    has_cover_image = filters.BooleanFilter(
        field_name="cover_image_url", lookup_expr="isnull", exclude=True
    )

    class Meta:
        model = AlbumModel
        fields = [
            "title",
            "artist_name",
            "artist_id",
            "source_type",
        ]
