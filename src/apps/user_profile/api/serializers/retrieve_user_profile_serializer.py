from rest_framework import serializers

from apps.user_profile.infrastructure.models.user_profile import UserProfile


class RetrieveUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "email",
        ]
        read_only_fields = fields
