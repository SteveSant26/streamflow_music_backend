from rest_framework import serializers


class UpcomingInvoiceSerializer(serializers.Serializer):
    id = serializers.CharField()
    amount_due = serializers.IntegerField()
    currency = serializers.CharField()
    period_start = serializers.IntegerField()
    period_end = serializers.IntegerField()
    due_date = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.CharField()


class UpcomingInvoiceWrapperSerializer(serializers.Serializer):
    invoice = UpcomingInvoiceSerializer(allow_null=True, required=False)
