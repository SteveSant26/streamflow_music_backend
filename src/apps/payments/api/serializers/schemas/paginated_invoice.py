from rest_framework import serializers

from ..invoice_serializers import InvoiceSerializer


class PaginatedInvoiceResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = InvoiceSerializer(many=True)
