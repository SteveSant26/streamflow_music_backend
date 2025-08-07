from django_filters import rest_framework as filters

from apps.payments.infrastructure.models import InvoiceModel


class InvoiceFilter(filters.FilterSet):
    user_email = filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    status = filters.ChoiceFilter(
        choices=[
            ("draft", "Borrador"),
            ("open", "Abierta"),
            ("paid", "Pagada"),
            ("uncollectible", "Incobrable"),
            ("void", "Anulada"),
        ]
    )
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr="lte")
    currency = filters.CharFilter(lookup_expr="iexact")
    due_after = filters.DateTimeFilter(field_name="due_date", lookup_expr="gte")
    due_before = filters.DateTimeFilter(field_name="due_date", lookup_expr="lte")
    paid_after = filters.DateTimeFilter(field_name="paid_at", lookup_expr="gte")
    paid_before = filters.DateTimeFilter(field_name="paid_at", lookup_expr="lte")
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = InvoiceModel
        fields = [
            "status",
            "currency",
        ]
