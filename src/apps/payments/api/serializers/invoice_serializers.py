from rest_framework import serializers

from apps.payments.domain.entities import InvoiceEntity
from common.serializers import BaseEntitySerializer

from ..dtos import InvoiceResponseDTO
from ..mappers import InvoiceEntityDTOMapper


class InvoiceSerializer(BaseEntitySerializer):
    """
    Serializer inteligente que hereda funcionalidad automática de conversión.
    Solo necesita definir las clases correspondientes.
    """

    # Configuración para el serializer base
    mapper_class = InvoiceEntityDTOMapper()  # type: ignore
    entity_class = InvoiceEntity
    dto_class = InvoiceResponseDTO

    # Definición de campos (opcional, solo para documentación/validación)
    id = serializers.CharField(read_only=True)
    stripe_invoice_id = serializers.CharField(read_only=True)
    amount = serializers.IntegerField(read_only=True)
    currency = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    due_date = serializers.DateTimeField(read_only=True, allow_null=True)
    paid_at = serializers.DateTimeField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)
