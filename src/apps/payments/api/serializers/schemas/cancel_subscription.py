from rest_framework import serializers


class CancelSubscriptionRequestSerializer(serializers.Serializer):
    subscription_id = serializers.CharField()


class CancelSubscriptionResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
