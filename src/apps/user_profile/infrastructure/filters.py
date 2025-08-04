from django_filters import rest_framework as filters

from apps.user_profile.infrastructure.models import UserProfileModel


class UserProfileFilter(filters.FilterSet):
    email = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = UserProfileModel
        fields = [
            "email",
        ]
