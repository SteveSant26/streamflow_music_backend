from django_filters import rest_framework as filters

from apps.payments.infrastructure.models import PaymentMethodModel


class PaymentMethodFilter(filters.FilterSet):
    user_email = filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    type = filters.CharFilter(lookup_expr="icontains")
    card_brand = filters.CharFilter(lookup_expr="icontains")
    card_last4 = filters.CharFilter(lookup_expr="exact")
    is_default = filters.BooleanFilter()
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = PaymentMethodModel
        fields = [
            "type",
            "card_brand",
            "is_default",
        ]
