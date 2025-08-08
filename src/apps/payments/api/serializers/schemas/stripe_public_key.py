from rest_framework import serializers


class StripePublicKeyResponseSerializer(serializers.Serializer):
    publishable_key = serializers.CharField()
