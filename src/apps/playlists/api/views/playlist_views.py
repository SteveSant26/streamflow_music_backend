from typing import List

from asgiref.sync import async_to_sync
from django.http import Http404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
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
from common.mixins import SimpleViewSetMixin
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
class PlaylistViewSet(SimpleViewSetMixin):
    """ViewSet para gestionar playlists"""

    queryset = PlaylistModel.objects.all()
    serializer_class = PlaylistResponseSerializer
    filterset_class = PlaylistModelFilter

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist_repository = PlaylistRepository()
        self.mapper = PlaylistEntityDTOMapper()

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

    def list(self, request):
        """Lista las playlists públicas y del usuario autenticado"""
        self.log_action(
            "list",
            f"user_id={request.user.id if request.user.is_authenticated else 'anonymous'}",
        )

        try:
            # Obtener parámetros de paginación
            limit = int(request.query_params.get("limit", 50))
            offset = int(request.query_params.get("offset", 0))

            # Configurar parámetros
            params = {"limit": limit, "offset": offset, "user_id": None}

            # Solo agregar user_id si el usuario está autenticado
            if request.user.is_authenticated:
                params["user_id"] = str(request.user.id)

            # Ejecutar caso de uso de manera sincrónica
            get_use_case = GetPublicAndUserPlaylistsUseCase(self.playlist_repository)
            playlists = async_to_sync(get_use_case.execute)(params)

            playlist_dtos = self.mapper.entities_to_dtos(playlists)
            serializer = PlaylistResponseSerializer(playlist_dtos, many=True)

            user_info = (
                f"user {request.user.id}"
                if request.user.is_authenticated
                else "anonymous user"
            )
            self.logger.info(f"Retrieved {len(playlists)} playlists for {user_info}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error listing playlists: {str(e)}")
            return Response(
                {"error": ERROR_LISTING_PLAYLISTS_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request):
        """Crea una nueva playlist"""
        self.log_action("create", f"user_id={request.user.id}")

        try:
            user_id = str(request.user.id)
            serializer = PlaylistCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Usar los datos del request después de la validación
            name = request.data.get("name", "")
            description = request.data.get("description")
            is_public = request.data.get("is_public", False)

            create_dto = CreatePlaylistRequestDTO(
                name=name,
                description=description,
                is_public=is_public,
            )

            use_case = CreatePlaylistUseCase(self.playlist_repository)
            playlist = async_to_sync(use_case.execute)(create_dto, user_id)

            playlist_dto = self.mapper.entity_to_dto(playlist)
            response_serializer = PlaylistResponseSerializer(playlist_dto)

            self.logger.info(f"Created playlist {playlist.id} for user {user_id}")
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.logger.error(f"Error creating playlist: {str(e)}")
            return Response(
                {"error": ERROR_CREATING_PLAYLIST_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, id=None):
        """Obtiene una playlist específica"""
        self.log_action("retrieve", f"user_id={request.user.id}, playlist_id={id}")

        try:
            if not id:
                raise Http404(PLAYLIST_NOT_FOUND_MSG)

            playlist_id = str(id)
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

        except Http404:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving playlist: {str(e)}")
            return Response(
                {"error": ERROR_RETRIEVING_PLAYLIST_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, id=None):
        """Actualiza una playlist"""
        self.log_action("update", f"user_id={request.user.id}, playlist_id={id}")

        try:
            if not id:
                raise Http404(PLAYLIST_NOT_FOUND_MSG)

            playlist_id = str(id)
            user_id = str(request.user.id)

            serializer = PlaylistUpdateSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Usar los datos del request después de la validación
            name = request.data.get("name")
            description = request.data.get("description")
            is_public = request.data.get("is_public")

            update_dto = UpdatePlaylistRequestDTO(
                playlist_id=playlist_id,
                name=name,
                description=description,
                is_public=is_public,
            )

            use_case = UpdatePlaylistUseCase(self.playlist_repository)
            playlist = async_to_sync(use_case.execute)(
                {
                    "playlist_id": playlist_id,
                    "user_id": user_id,
                    "update_dto": update_dto,
                }
            )

            playlist_dto = self.mapper.entity_to_dto(playlist)
            response_serializer = PlaylistResponseSerializer(playlist_dto)

            self.logger.info(f"Updated playlist {playlist_id} for user {user_id}")
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error updating playlist: {str(e)}")
            return Response(
                {"error": ERROR_UPDATING_PLAYLIST_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, id=None):
        """Elimina una playlist"""
        self.log_action("destroy", f"user_id={request.user.id}, playlist_id={id}")

        try:
            if not id:
                raise Http404(PLAYLIST_NOT_FOUND_MSG)

            playlist_id = str(id)
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

        except Exception as e:
            self.logger.error(f"Error deleting playlist: {str(e)}")
            return Response(
                {"error": ERROR_DELETING_PLAYLIST_MSG},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
