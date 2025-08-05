from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.playlists.api.serializers import (
    PlaylistCreateSerializer,
    PlaylistResponseSerializer,
    PlaylistUpdateSerializer,
)
from apps.playlists.infrastructure.repository import PlaylistRepository
from apps.playlists.use_cases import (
    CreatePlaylistUseCase,
    DeletePlaylistUseCase,
    EnsureDefaultPlaylistUseCase,
    GetUserPlaylistsUseCase,
    UpdatePlaylistUseCase,
)
from common.mixins import LoggingMixin


class PlaylistViewSet(LoggingMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar playlists"""

    serializer_class = PlaylistResponseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist_repository = PlaylistRepository()

    def get_queryset(self):
        """Override para filtrar por usuario"""
        # Retornamos queryset vacío ya que manejamos datos via use cases
        from apps.playlists.infrastructure.models import PlaylistModel

        if not hasattr(self, "_queryset_cache"):
            self._queryset_cache = PlaylistModel.objects.none()
        return self._queryset_cache

    def list(self, request):
        """Lista las playlists del usuario autenticado"""
        try:
            user_id = str(request.user.id)

            # Usar asgiref para ejecutar código async
            import asyncio

            async def get_playlists():
                # Asegurar que existe la playlist de favoritos
                ensure_favorites_use_case = EnsureDefaultPlaylistUseCase(
                    self.playlist_repository
                )
                await ensure_favorites_use_case.execute(user_id)

                # Obtener playlists del usuario
                get_playlists_use_case = GetUserPlaylistsUseCase(
                    self.playlist_repository
                )
                return await get_playlists_use_case.execute(user_id)

            # Ejecutar async code
            playlists = asyncio.run(get_playlists())

            # Convertir a DTOs
            from apps.playlists.api.mappers import PlaylistEntityDTOMapper

            mapper = PlaylistEntityDTOMapper()
            playlist_dtos = [mapper.entity_to_dto(playlist) for playlist in playlists]

            # Serializar respuesta
            serializer = PlaylistResponseSerializer(playlist_dtos, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error listing playlists: {str(e)}")
            return Response(
                {"error": "Error obteniendo playlists"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def create(self, request):
        """Crea una nueva playlist"""
        try:
            user_id = str(request.user.id)

            # Validar datos de entrada
            serializer = PlaylistCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Obtener datos validados de forma segura
            validated_data = serializer.validated_data or {}
            name = validated_data.get("name", "")
            description = validated_data.get("description")
            is_public = validated_data.get("is_public", False)

            # Crear DTO manualmente
            from apps.playlists.api.dtos import CreatePlaylistRequestDTO

            create_dto = CreatePlaylistRequestDTO(
                name=name,
                description=description,
                is_public=is_public,
            )

            # Ejecutar use case
            import asyncio

            async def create_playlist():
                create_use_case = CreatePlaylistUseCase(self.playlist_repository)
                return await create_use_case.execute(create_dto, user_id)

            playlist = asyncio.run(create_playlist())

            # Convertir a DTO y serializar
            from apps.playlists.api.mappers import PlaylistEntityDTOMapper

            mapper = PlaylistEntityDTOMapper()
            playlist_dto = mapper.entity_to_dto(playlist)

            response_serializer = PlaylistResponseSerializer(playlist_dto)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.logger.error(f"Error creating playlist: {str(e)}")
            return Response(
                {"error": "Error creando playlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def retrieve(self, request, id=None):
        """Obtiene una playlist específica"""
        try:
            if not id:
                raise Http404("Playlist no encontrada")

            playlist_id = str(id)
            user_id = str(request.user.id)

            # Obtener playlists del usuario
            import asyncio

            async def get_user_playlist():
                get_playlists_use_case = GetUserPlaylistsUseCase(
                    self.playlist_repository
                )
                playlists = await get_playlists_use_case.execute(user_id)
                for playlist in playlists:
                    if playlist.id == playlist_id:
                        return playlist
                return None

            playlist = asyncio.run(get_user_playlist())
            if not playlist:
                raise Http404("Playlist no encontrada")

            # Convertir a DTO y serializar
            from apps.playlists.api.mappers import PlaylistEntityDTOMapper

            mapper = PlaylistEntityDTOMapper()
            playlist_dto = mapper.entity_to_dto(playlist)

            serializer = PlaylistResponseSerializer(playlist_dto)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Http404:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving playlist: {str(e)}")
            return Response(
                {"error": "Error obteniendo playlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def update(self, request, id=None):
        """Actualiza una playlist"""
        try:
            if not id:
                raise Http404("Playlist no encontrada")

            playlist_id = str(id)
            user_id = str(request.user.id)

            # Validar datos de entrada
            serializer = PlaylistUpdateSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Crear DTO manualmente
            validated_data = serializer.validated_data or {}
            from apps.playlists.api.dtos import UpdatePlaylistRequestDTO

            update_dto = UpdatePlaylistRequestDTO(
                playlist_id=playlist_id,
                name=validated_data.get("name") if validated_data else None,
                description=validated_data.get("description")
                if validated_data
                else None,
                is_public=validated_data.get("is_public") if validated_data else None,
            )

            # Ejecutar use case
            import asyncio

            async def update_playlist():
                update_use_case = UpdatePlaylistUseCase(self.playlist_repository)
                return await update_use_case.execute(
                    {
                        "playlist_id": playlist_id,
                        "user_id": user_id,
                        "update_dto": update_dto,
                    }
                )

            playlist = asyncio.run(update_playlist())

            # Convertir a DTO y serializar
            from apps.playlists.api.mappers import PlaylistEntityDTOMapper

            mapper = PlaylistEntityDTOMapper()
            playlist_dto = mapper.entity_to_dto(playlist)

            response_serializer = PlaylistResponseSerializer(playlist_dto)
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error updating playlist: {str(e)}")
            return Response(
                {"error": "Error actualizando playlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, id=None):
        """Elimina una playlist"""
        try:
            if not id:
                raise Http404("Playlist no encontrada")

            playlist_id = str(id)

            # Ejecutar use case
            import asyncio

            async def delete_playlist():
                delete_use_case = DeletePlaylistUseCase(self.playlist_repository)
                return await delete_use_case.execute(playlist_id)

            result = asyncio.run(delete_playlist())

            if result:
                return Response(
                    {"message": "Playlist eliminada exitosamente"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    {"error": "No se pudo eliminar la playlist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            self.logger.error(f"Error deleting playlist: {str(e)}")
            return Response(
                {"error": "Error eliminando playlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
