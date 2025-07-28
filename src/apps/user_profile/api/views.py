from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.user_profile.api.serializers import (
    RetrieveUserProfileSerializer,
    UploadProfilePictureSerializer,
)
from apps.user_profile.infrastructure.models.user_profile import UserProfile
from common.utils.image_utils import ImageUtils
from src.common.utils import get_logger

from ..infrastructure.repository import UserRepository
from ..use_cases import GetUserProfile, UploadProfilePicture

logger = get_logger(__name__)

user_repository = UserRepository()
image_utils = ImageUtils("profile-pictures")


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["get", "post", "put", "delete"]

    def get_permission(self):
        if self.action in ["me", "upload_profile_picture"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        action_to_serializer = {
            "me": RetrieveUserProfileSerializer,
            "upload_profile_picture": UploadProfilePictureSerializer,
        }
        return action_to_serializer.get(self.action, RetrieveUserProfileSerializer)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        logger.info(f"User {request.user.id} is requesting their profile.")

        get_user_profile = GetUserProfile(user_repository)

        user_entity = get_user_profile.execute(request.user.id)
        serializer = RetrieveUserProfileSerializer(user_entity)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="upload-profile-picture")
    def upload_profile_picture(self, request):
        logger.info(f"User {request.user.id} is uploading a profile picture.")
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        profile_picture_file = serializer.validated_data["profile_picture"]

        upload_profile_picture = UploadProfilePicture(user_repository, image_utils)

        user_entity = upload_profile_picture.execute(
            {
                "id": request.user.id,
                "profile_picture": profile_picture_file,
                "email": request.user.email,
            }
        )
        if not user_entity:
            return Response(
                {"detail": "Failed to upload profile picture."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            RetrieveUserProfileSerializer(user_entity).data, status=status.HTTP_200_OK
        )
