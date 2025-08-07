from django_filters import rest_framework as filters

from apps.payments.infrastructure.models import PaymentMethodModel, PaymentModel


class PaymentFilter(filters.FilterSet):
    user_email = filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    status = filters.ChoiceFilter(
        choices=[
            ("succeeded", "Exitoso"),
            ("pending", "Pendiente"),
            ("failed", "Fallido"),
            ("canceled", "Cancelado"),
        ]
    )
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr="lte")
    currency = filters.CharFilter(lookup_expr="iexact")
    payment_method = filters.ModelChoiceFilter(
        queryset=PaymentMethodModel.objects.all()
    )
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = PaymentModel
        fields = [
            "status",
            "currency",
            "payment_method",
        ]
