from rest_framework import serializers

from apps.user_profile.infrastructure.models.user_profile import UserProfile
from src.common.utils import ImageUtils


class RetrieveUserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "email",
            "profile_picture",
        ]
        read_only_fields = fields

    def get_profile_picture(self, obj):
        """
        Returns the URL of the profile picture if it exists, otherwise returns None.
        """
        if obj.profile_picture:
            return ImageUtils("profile-pictures").get_image_url(obj.profile_picture)
        return None
