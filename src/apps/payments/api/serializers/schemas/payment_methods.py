from rest_framework import serializers

from ..payment_method_serializers import PaymentMethodSerializer


class PaymentMethodsResponseSerializer(serializers.Serializer):
    payment_methods = PaymentMethodSerializer(many=True)
