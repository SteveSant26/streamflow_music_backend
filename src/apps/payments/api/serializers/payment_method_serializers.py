from rest_framework import serializers

from ...infrastructure.models.payment_method import PaymentMethodModel


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethodModel
        fields = [
            "id",
            "user",
            "stripe_payment_method_id",
            "type",
            "card_brand",
            "card_last4",
            "card_exp_month",
            "card_exp_year",
            "is_default",
            "created_at",
        ]
        read_only_fields = ("id", "created_at", "user")
