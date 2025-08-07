from django_filters import rest_framework as filters

from apps.payments.infrastructure.models import SubscriptionModel, SubscriptionPlanModel


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
