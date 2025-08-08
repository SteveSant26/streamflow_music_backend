from rest_framework import serializers


class CheckoutSessionRequestSerializer(serializers.Serializer):
    plan_id = serializers.CharField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()
    allow_promotion_codes = serializers.BooleanField(required=False, default=True)
    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class CheckoutSessionResponseSerializer(serializers.Serializer):
    url = serializers.URLField()
    session_id = serializers.CharField()
