from django_filters import rest_framework as filters

from apps.genres.infrastructure.models.genre_model import GenreModel


class GenreModelFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    min_popularity_score = filters.NumberFilter(
        field_name="popularity_score", lookup_expr="gte"
    )
    max_popularity_score = filters.NumberFilter(
        field_name="popularity_score", lookup_expr="lte"
    )
    has_description = filters.BooleanFilter(
        field_name="description", lookup_expr="isnull", exclude=True
    )
    has_image = filters.BooleanFilter(
        field_name="image_url", lookup_expr="isnull", exclude=True
    )
    has_color = filters.BooleanFilter(
        field_name="color_hex", lookup_expr="isnull", exclude=True
    )
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = GenreModel
        fields = [
            "name",
        ]
