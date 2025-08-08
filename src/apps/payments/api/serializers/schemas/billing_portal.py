from rest_framework import serializers


class BillingPortalRequestSerializer(serializers.Serializer):
    return_url = serializers.URLField()


class BillingPortalResponseSerializer(serializers.Serializer):
    url = serializers.URLField()
