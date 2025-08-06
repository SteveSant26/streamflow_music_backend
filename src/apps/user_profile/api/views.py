from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.response import Response

from apps.playlists.api.mappers import PlaylistEntityDTOMapper
from apps.playlists.api.serializers import PlaylistResponseSerializer
from apps.playlists.infrastructure.repository import PlaylistRepository
from apps.playlists.use_cases import (
    EnsureDefaultPlaylistUseCase,
    GetUserPlaylistsUseCase,
)
from apps.user_profile.api.mappers import UserProfileMapper
from apps.user_profile.api.serializers import (
    RetrieveUserProfileSerializer,
    UploadProfilePictureSerializer,
)
from apps.user_profile.infrastructure.filters import UserProfileFilter
from apps.user_profile.infrastructure.models.user_profile import UserProfileModel
from common.factories import StorageServiceFactory
from common.mixins import CRUDViewSetMixin
from src.apps.user_profile.infrastructure.permissions import IsPlaylistOwner

from ..api.dtos import UploadProfilePictureRequestDTO
from ..infrastructure.repository import UserRepository
from ..use_cases import GetUserProfileUseCase, UploadProfilePicture


@extend_schema_view(
    list=extend_schema(
        tags=["User Profile"], description="List user profiles with optional filtering"
    ),
    retrieve=extend_schema(
        tags=["User Profile"], description="Get a specific user profile by ID"
    ),
    create=extend_schema(
        tags=["User Profile"],
        description="Profile creation is blocked - profiles are created automatically",
    ),
    update=extend_schema(tags=["User Profile"], description="Update user profile"),
    destroy=extend_schema(tags=["User Profile"], description="Delete user profile"),
    me=extend_schema(tags=["User Profile"], description="Get current user's profile"),
    upload_profile_picture=extend_schema(
        tags=["User Profile"], description="Upload a new profile picture"
    ),
    playlists=extend_schema(tags=["User Profile"], description="Get user's playlists"),
)
class UserProfileViewSet(CRUDViewSetMixin):
    queryset = UserProfileModel.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["get", "post", "delete"]
    filterset_class = UserProfileFilter
    ordering = ["email"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user_repository = UserRepository()
        self.playlist_repository = PlaylistRepository()
        self.playlist_mapper = PlaylistEntityDTOMapper()
        self.storage_service = StorageServiceFactory.create_profile_pictures_service()
        self.mapper = UserProfileMapper()

    def get_permissions(self) -> list[BasePermission]:
        action_permissions = {
            "me": [IsAuthenticated],
            "upload_profile_picture": [IsAuthenticated],
            "update": [IsAuthenticated],
            "partial_update": [IsAuthenticated],
            "destroy": [IsAuthenticated],
            "playlists": [IsPlaylistOwner],
        }
        permission_classes = action_permissions.get(self.action, [AllowAny])
        return [permission() for permission in permission_classes]

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
        get_user_profile = GetUserProfileUseCase(self.user_repository)
        user_entity = async_to_sync(get_user_profile.execute)(str(request.user.id))

        # Convertir entidad a DTO usando el mapper
        user_dto = self.mapper.entity_to_dto(user_entity)
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
            self.user_repository, self.storage_service
        )
        user_entity = async_to_sync(upload_profile_picture_use_case.execute)(
            request_dto
        )

        self.logger.info(
            f"Profile picture uploaded successfully for user {request.user.id}."
        )

        # Convertir entidad a DTO usando el mapper
        user_dto = self.mapper.entity_to_dto(user_entity)
        return Response(
            RetrieveUserProfileSerializer(user_dto).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="playlists",
    )
    def playlists(
        self,
        request,
    ):
        """Obtiene todas las playlists de un usuario específico"""
        user_id = str(request.user.id)
        self.logger.info(f"Requesting playlists for user ID: {user_id}")

        # Asegurar que existe la playlist por defecto
        ensure_use_case = EnsureDefaultPlaylistUseCase(self.playlist_repository)
        async_to_sync(ensure_use_case.execute)(user_id)

        # Obtener playlists del usuario
        get_use_case = GetUserPlaylistsUseCase(self.playlist_repository)
        playlists = async_to_sync(get_use_case.execute)(user_id)

        # Convertir a DTOs y serializar
        playlist_dtos = self.playlist_mapper.entities_to_dtos(playlists)
        serializer = PlaylistResponseSerializer(playlist_dtos, many=True)

        self.logger.info(f"Retrieved {len(playlists)} playlists for user {user_id}")
        return Response(serializer.data, status=status.HTTP_200_OK)
