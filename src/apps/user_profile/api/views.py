from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.user_profile.api.serializers import RetrieveUserProfileSerializer
from src.common.utils import get_logger

from ..infrastructure.repository import UserRepository
from ..use_cases import GetUserProfile

logger = get_logger(__name__)


class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        logger.info(f"User {request.user.id} is requesting their profile.")

        user_repository = UserRepository()
        get_user_profile = GetUserProfile(user_repository)

        user_entity = get_user_profile.execute(request.user.id)
        serializer = RetrieveUserProfileSerializer(user_entity)
        return Response(serializer.data, status=status.HTTP_200_OK)
