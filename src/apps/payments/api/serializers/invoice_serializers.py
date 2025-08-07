from rest_framework import serializers


class InvoiceSerializer(serializers.Serializer):
    """Serializador para las facturas"""

    id = serializers.CharField(read_only=True)
    stripe_invoice_id = serializers.CharField(read_only=True)
    amount = serializers.IntegerField(read_only=True)
    currency = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    due_date = serializers.DateTimeField(read_only=True, allow_null=True)
    paid_at = serializers.DateTimeField(read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, allow_null=True)

    def to_representation(self, instance):
        """Convertir entidad a representación JSON"""
        return {
            "id": instance.id,
            "stripe_invoice_id": instance.stripe_invoice_id,
            "amount": instance.amount,
            "currency": instance.currency,
            "status": instance.status.value
            if hasattr(instance.status, "value")
            else instance.status,
            "due_date": instance.due_date.isoformat() if instance.due_date else None,
            "paid_at": instance.paid_at.isoformat() if instance.paid_at else None,
            "created_at": instance.created_at.isoformat()
            if instance.created_at
            else None,
        }
