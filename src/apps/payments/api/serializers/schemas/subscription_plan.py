from rest_framework import serializers


class SubscriptionPlanSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.IntegerField()
    currency = serializers.CharField()
    interval = serializers.CharField()
    interval_count = serializers.IntegerField()
    features = serializers.ListField(child=serializers.CharField())
    stripe_price_id = serializers.CharField()
    is_active = serializers.BooleanField()


class SubscriptionPlansResponseSerializer(serializers.Serializer):
    plans = SubscriptionPlanSerializer(many=True)
