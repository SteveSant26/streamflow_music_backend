from rest_framework import serializers

from apps.payments.domain.entities import PaymentMethodEntity
from common.serializers import BaseEntitySerializer

from ..dtos import PaymentMethodResponseDTO
from ..mappers import PaymentMethodEntityDTOMapper


class PaymentMethodSerializer(BaseEntitySerializer):
    """
    Serializer inteligente que hereda funcionalidad automática de conversión.
    Solo necesita definir las clases correspondientes.
    """

    # Configuración para el serializer base
    mapper_class = PaymentMethodEntityDTOMapper()  # type: ignore
    entity_class = PaymentMethodEntity
    dto_class = PaymentMethodResponseDTO

    # Definición de campos (opcional, solo para documentación/validación)
    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(read_only=True)
    stripe_payment_method_id = serializers.CharField(read_only=True)
    type = serializers.CharField(read_only=True)
    card_brand = serializers.CharField(read_only=True, allow_null=True)
    card_last4 = serializers.CharField(read_only=True, allow_null=True)
    card_exp_month = serializers.IntegerField(read_only=True, allow_null=True)
    card_exp_year = serializers.IntegerField(read_only=True, allow_null=True)
    is_default = serializers.BooleanField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)
