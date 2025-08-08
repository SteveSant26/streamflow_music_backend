from rest_framework import serializers


class UserSubscriptionSerializer(serializers.Serializer):
    id = serializers.CharField()
    user_id = serializers.CharField()
    plan_id = serializers.CharField()
    stripe_subscription_id = serializers.CharField()
    stripe_customer_id = serializers.CharField()
    status = serializers.CharField()
    current_period_start = serializers.DateTimeField()
    current_period_end = serializers.DateTimeField()
    trial_start = serializers.DateTimeField(required=False, allow_null=True)
    trial_end = serializers.DateTimeField(required=False, allow_null=True)
    canceled_at = serializers.DateTimeField(required=False, allow_null=True)
    is_active = serializers.BooleanField()
    is_on_trial = serializers.BooleanField()


class UserSubscriptionWrapperSerializer(serializers.Serializer):
    subscription = UserSubscriptionSerializer(allow_null=True, required=False)
