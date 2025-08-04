from django_filters import rest_framework as filters

from apps.artists.infrastructure.models.artist_model import ArtistModel


class ArtistModelFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    country = filters.CharFilter(lookup_expr="icontains")
    min_followers_count = filters.NumberFilter(
        field_name="followers_count", lookup_expr="gte"
    )
    max_followers_count = filters.NumberFilter(
        field_name="followers_count", lookup_expr="lte"
    )
    is_verified = filters.BooleanFilter()
    source_type = filters.ChoiceFilter(
        choices=[
            ("manual", "Manual"),
            ("youtube", "YouTube"),
            ("spotify", "Spotify"),
            ("soundcloud", "SoundCloud"),
        ]
    )
    has_biography = filters.BooleanFilter(
        field_name="biography", lookup_expr="isnull", exclude=True
    )
    has_image = filters.BooleanFilter(
        field_name="image_url", lookup_expr="isnull", exclude=True
    )
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = ArtistModel
        fields = [
            "name",
            "country",
            "is_verified",
            "source_type",
        ]
