from rest_framework import serializers

from ...infrastructure.models import UserProfile


class UploadProfilePictureSerializer(serializers.ModelSerializer):
    """
    Serializer for uploading a profile picture.
    """

    profile_picture = serializers.ImageField(required=True, allow_empty_file=False)

    def validate_profile_picture(self, value):
        """
        Custom validation for the image field.
        """
        if value.size > 5 * 1024 * 1024:  # 5 MB limit
            raise serializers.ValidationError("Image size must be less than 5 MB.")
        return value

    class Meta:
        model = UserProfile
        fields = ["profile_picture"]
