from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.user_profile.api.serializers import (
    RetrieveUserProfileSerializer,
    UploadProfilePictureSerializer,
)
from apps.user_profile.infrastructure.models.user_profile import UserProfileModel
from common.factories import StorageServiceFactory
from common.mixins.logging_mixin import LoggingMixin

from ..api.dtos import UploadProfilePictureRequestDTO
from ..api.mappers import UserProfileMapper
from ..infrastructure.repository import UserRepository
from ..use_cases import GetUserProfileUseCase, UploadProfilePicture

# Instancias globales (idealmente esto debería ser inyección de dependencias)
user_repository = UserRepository()
storage_service = StorageServiceFactory.create_profile_pictures_service()


@extend_schema_view(
    list=extend_schema(tags=["User Profile"]),
    retrieve=extend_schema(tags=["User Profile"]),
    create=extend_schema(tags=["User Profile"]),
    update=extend_schema(tags=["User Profile"]),
    destroy=extend_schema(tags=["User Profile"]),
    me=extend_schema(tags=["User Profile"], description="Get current user's profile"),
    upload_profile_picture=extend_schema(
        tags=["User Profile"], description="Upload a new profile picture"
    ),
)
class UserProfileViewSet(viewsets.ModelViewSet, LoggingMixin):
    queryset = UserProfileModel.objects.all()
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["get", "post", "delete"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper = UserProfileMapper()

    def get_permissions(self):
        action_permissions = {
            "me": IsAuthenticated,
            "upload_profile_picture": IsAuthenticated,
            "update": IsAuthenticated,
            "partial_update": IsAuthenticated,
            "destroy": IsAuthenticated,
        }
        permission_class = action_permissions.get(self.action, AllowAny)
        return [permission_class()]

    def get_serializer_class(self):
        action_to_serializer = {
            "me": RetrieveUserProfileSerializer,
            "upload_profile_picture": UploadProfilePictureSerializer,
        }
        return action_to_serializer.get(self.action, RetrieveUserProfileSerializer)

    def create(self, request, *args, **kwargs):
        """
        Bloquea la creación de perfiles ya que se crean automáticamente.
        """
        return Response(
            {
                "detail": "Profile creation is not allowed. Profiles are created automatically."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        self.logger.info(f"User {request.user.id} is requesting their profile.")

        # Usar caso de uso
        get_user_profile = GetUserProfileUseCase(user_repository)
        user_entity = async_to_sync(get_user_profile.execute)(str(request.user.id))

        # Convertir entidad a DTO usando el mapper
        user_dto = self.mapper.entity_to_response_dto(user_entity)
        serializer = self.get_serializer(user_dto)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="upload-profile-picture")
    def upload_profile_picture(self, request):
        self.logger.info(f"User {request.user.id} is uploading a profile picture.")

        # Validar datos de entrada
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        profile_picture_file = serializer.validated_data["profile_picture"]

        # Crear DTO para el caso de uso
        request_dto = UploadProfilePictureRequestDTO(
            user_id=str(request.user.id),
            email=request.user.email,
            profile_picture_file=profile_picture_file,
        )

        # Usar caso de uso
        upload_profile_picture_use_case = UploadProfilePicture(
            user_repository, storage_service
        )
        user_entity = async_to_sync(upload_profile_picture_use_case.execute)(
            request_dto
        )

        self.logger.info(
            f"Profile picture uploaded successfully for user {request.user.id}."
        )

        # Convertir entidad a DTO usando el mapper
        user_dto = self.mapper.entity_to_response_dto(user_entity)
        return Response(
            RetrieveUserProfileSerializer(user_dto).data,
            status=status.HTTP_200_OK,
        )
