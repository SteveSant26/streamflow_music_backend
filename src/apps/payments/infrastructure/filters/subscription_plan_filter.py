from django_filters import rest_framework as filters

from apps.payments.infrastructure.models import SubscriptionPlanModel


class SubscriptionPlanFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains")
    min_price = filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = filters.NumberFilter(field_name="price", lookup_expr="lte")
    currency = filters.CharFilter(lookup_expr="iexact")
    interval = filters.ChoiceFilter(choices=[("month", "Mensual"), ("year", "Anual")])
    is_active = filters.BooleanFilter()
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = SubscriptionPlanModel
        fields = [
            "name",
            "currency",
            "interval",
            "is_active",
        ]
