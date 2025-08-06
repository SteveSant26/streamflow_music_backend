from typing import List

from asgiref.sync import async_to_sync
from django.http import Http404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.playlists.api.serializers import (
    PlaylistCreateSerializer,
    PlaylistResponseSerializer,
    PlaylistUpdateSerializer,
)
from apps.playlists.infrastructure.filters import PlaylistModelFilter
from apps.playlists.infrastructure.models.playlist_model import PlaylistModel
from apps.playlists.infrastructure.repository import PlaylistRepository
from apps.playlists.use_cases import (
    CreatePlaylistUseCase,
    DeletePlaylistUseCase,
    GetPublicAndUserPlaylistsUseCase,
    GetUserPlaylistsUseCase,
    UpdatePlaylistUseCase,
)
from apps.user_profile.infrastructure.permissions import (
    IsPlaylistOwner,
    IsPlaylistOwnerOrPublic,
)
from src.common.factories.storage_service_factory import StorageServiceFactory
from src.common.mixins.crud_viewset_mixin import CRUDViewSetMixin
from src.common.utils.schema_decorators import paginated_list_endpoint

from ..dtos import CreatePlaylistRequestDTO, UpdatePlaylistRequestDTO
from ..mappers import PlaylistEntityDTOMapper

# Constantes para mensajes de error
PLAYLIST_NOT_FOUND_MSG = "Playlist no encontrada"
ERROR_LISTING_PLAYLISTS_MSG = "Error obteniendo playlists"
ERROR_CREATING_PLAYLIST_MSG = "Error creando playlist"
ERROR_RETRIEVING_PLAYLIST_MSG = "Error obteniendo playlist"
ERROR_UPDATING_PLAYLIST_MSG = "Error actualizando playlist"
ERROR_DELETING_PLAYLIST_MSG = "Error eliminando playlist"
DELETE_FAILED_MSG = "No se pudo eliminar la playlist"


@extend_schema_view(
    list=extend_schema(
        tags=["Playlist"],
        description="List public playlists and user playlists (if authenticated).",
    ),
    retrieve=extend_schema(
        tags=["Playlist"], description="Get a specific user playlist by ID"
    ),
    create=extend_schema(
        tags=["Playlist"],
        description="Create a new playlist (authentication required)",
    ),
    update=extend_schema(
        tags=["Playlist"], description="Update user playlist (authentication required)"
    ),
    destroy=extend_schema(
        tags=["Playlist"], description="Delete user playlist (authentication required)"
    ),
)
class PlaylistViewSet(CRUDViewSetMixin):
    """ViewSet para gestionar playlists"""

    queryset = PlaylistModel.objects.all()
    serializer_class = PlaylistResponseSerializer
    filterset_class = PlaylistModelFilter
    http_method_names = ["get", "post", "put", "delete"]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist_repository = PlaylistRepository()
        self.storage_service = StorageServiceFactory.create_playlist_images_service()
        self.mapper = PlaylistEntityDTOMapper()

    def get_serializer_class(self) -> type:
        if self.action == "create":
            return PlaylistCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return PlaylistUpdateSerializer
        return PlaylistResponseSerializer

    def get_permissions(self) -> List:
        """
        Define permisos específicos por acción.
        - list: Acceso libre (AllowAny)
        - create: Requiere autenticación
        - retrieve: Propietario o playlist pública
        - update, partial_update: Solo propietario
        - destroy: Solo propietario
        """
        action_permissions = {
            "create": [IsAuthenticated],
            "retrieve": [IsPlaylistOwnerOrPublic],
            "update": [IsPlaylistOwner],
            "partial_update": [IsPlaylistOwner],
            "destroy": [IsPlaylistOwner],
        }
        permission_classes = action_permissions.get(self.action, [AllowAny])
        return [permission() for permission in permission_classes]

    @paginated_list_endpoint(
        serializer_class=PlaylistResponseSerializer,
        tags=["Playlists"],
        description="Get popular playlists from the database",
    )
    def list(self, request):
        """Lista las playlists públicas y del usuario autenticado"""
        self.logger.debug(
            f"user_id={request.user.id if request.user.is_authenticated else 'anonymous'}",
        )

        # Configurar parámetros sin límites - DRF se encarga de la paginación
        params = {}

        # Solo agregar user_id si el usuario está autenticado
        if request.user.is_authenticated:
            params["user_id"] = str(request.user.id)

        # Ejecutar caso de uso de manera sincrónica
        get_use_case = GetPublicAndUserPlaylistsUseCase(self.playlist_repository)
        playlists = async_to_sync(get_use_case.execute)(params)

        user_info = (
            f"user {request.user.id}"
            if request.user.is_authenticated
            else "anonymous user"
        )
        # Usar la paginación de DRF
        page = self.paginate_queryset(playlists)
        if page is not None:
            playlist_dtos = self.mapper.entities_to_dtos(page)
            serializer = PlaylistResponseSerializer(playlist_dtos, many=True)
            self.logger.info(f"Retrieved {len(page)} playlists for {user_info}")
            return self.get_paginated_response(serializer.data)

        # Fallback sin paginación si no se puede paginar
        playlist_dtos = self.mapper.entities_to_dtos(playlists)
        serializer = PlaylistResponseSerializer(playlist_dtos, many=True)

        self.logger.info(f"Retrieved {len(playlists)} playlists for {user_info}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """Crea una nueva playlist"""
        self.logger.debug(f"user_id={request.user.id}")

        user_id = str(request.user.id)
        serializer = PlaylistCreateSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            print(serializer.errors)
            print(serializer.errors)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name", "")
        description = request.data.get("description")
        is_public = request.data.get("is_public", False)
        playlist_img_file = serializer.validated_data.get("playlist_img")  # type: ignore

        create_dto = CreatePlaylistRequestDTO(
            name=name,
            description=description,
            is_public=is_public,
            playlist_img_file=playlist_img_file,
        )

        use_case = CreatePlaylistUseCase(self.playlist_repository, self.storage_service)
        playlist = async_to_sync(use_case.execute)(create_dto, user_id)

        playlist_dto = self.mapper.entity_to_dto(playlist)
        response_serializer = PlaylistResponseSerializer(playlist_dto)

        self.logger.info(f"Created playlist {playlist.id} for user {user_id}")
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """Obtiene una playlist específica"""
        self.logger.debug(f"user_id={request.user.id}, playlist_id={pk}")

        if not pk:
            raise Http404(PLAYLIST_NOT_FOUND_MSG)

        playlist_id = str(pk)
        user_id = str(request.user.id)

        get_use_case = GetUserPlaylistsUseCase(self.playlist_repository)
        playlists = async_to_sync(get_use_case.execute)(user_id)

        playlist = next((p for p in playlists if p.id == playlist_id), None)
        if not playlist:
            raise Http404(PLAYLIST_NOT_FOUND_MSG)

        playlist_dto = self.mapper.entity_to_dto(playlist)
        serializer = PlaylistResponseSerializer(playlist_dto)

        self.logger.info(f"Retrieved playlist {playlist_id} for user {user_id}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """Actualiza una playlist"""
        self.logger.debug(f"user_id={request.user.id}, playlist_id={pk}")

        if not pk:
            raise Http404(PLAYLIST_NOT_FOUND_MSG)

        playlist_id = str(pk)
        user_id = str(request.user.id)

        serializer = PlaylistUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        name = request.data.get("name")
        description = request.data.get("description")
        is_public = request.data.get("is_public")
        playlist_img_file = serializer.validated_data.get("playlist_img_file")  # type: ignore

        update_dto = UpdatePlaylistRequestDTO(
            playlist_id=playlist_id,
            name=name,
            description=description,
            is_public=is_public,
            playlist_img_file=playlist_img_file,
        )

        use_case = UpdatePlaylistUseCase(self.playlist_repository, self.storage_service)
        playlist = async_to_sync(use_case.execute)(user_id, update_dto)

        playlist_dto = self.mapper.entity_to_dto(playlist)

        self.logger.info(f"Updated playlist {playlist_id} for user {user_id}")
        return Response(
            PlaylistResponseSerializer(playlist_dto).data, status=status.HTTP_200_OK
        )

    def destroy(self, request, pk=None):
        """Elimina una playlist"""
        self.logger.debug("destroy", f"user_id={request.user.id}, playlist_id={pk}")

        if not pk:
            raise Http404(PLAYLIST_NOT_FOUND_MSG)

        playlist_id = str(pk)
        use_case = DeletePlaylistUseCase(self.playlist_repository)
        result = async_to_sync(use_case.execute)(playlist_id)

        if result:
            self.logger.info(f"Deleted playlist {playlist_id}")
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"error": DELETE_FAILED_MSG},
                status=status.HTTP_400_BAD_REQUEST,
            )
