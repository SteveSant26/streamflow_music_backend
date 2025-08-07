from django_filters import rest_framework as filters

from apps.payments.infrastructure.models import (
    InvoiceModel,
    PaymentMethodModel,
    PaymentModel,
    SubscriptionModel,
    SubscriptionPlanModel,
)


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


class SubscriptionFilter(filters.FilterSet):
    status = filters.ChoiceFilter(
        choices=[
            ("active", "Activa"),
            ("canceled", "Cancelada"),
            ("incomplete", "Incompleta"),
            ("incomplete_expired", "Incompleta Expirada"),
            ("past_due", "Vencida"),
            ("unpaid", "Sin Pagar"),
            ("trialing", "En Prueba"),
        ]
    )
    plan = filters.ModelChoiceFilter(queryset=SubscriptionPlanModel.objects.all())
    user_email = filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    period_start_after = filters.DateTimeFilter(
        field_name="current_period_start", lookup_expr="gte"
    )
    period_start_before = filters.DateTimeFilter(
        field_name="current_period_start", lookup_expr="lte"
    )
    period_end_after = filters.DateTimeFilter(
        field_name="current_period_end", lookup_expr="gte"
    )
    period_end_before = filters.DateTimeFilter(
        field_name="current_period_end", lookup_expr="lte"
    )
    is_on_trial = filters.BooleanFilter(
        field_name="trial_end", lookup_expr="isnull", exclude=True
    )
    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = SubscriptionModel
        fields = [
            "status",
            "plan",
            "user_email",
        ]


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
