from uuid import UUID

from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
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
from common.mixins.crud_viewset_mixin import CRUDViewSetMixin


class PlaylistViewSet(CRUDViewSetMixin):
    """ViewSet para gestionar playlists"""
    
    serializer_class = PlaylistResponseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist_repository = PlaylistRepository()
    
    def get_queryset(self):
        """Override para filtrar por usuario"""
        return []  # No usamos queryset tradicional
    
    def list(self, request):
        """Lista las playlists del usuario autenticado"""
        user_id = UUID(str(request.user.id))
        
        # Asegurar que existe la playlist de favoritos
        ensure_favorites_use_case = EnsureDefaultPlaylistUseCase(self.playlist_repository)
        
        get_playlists_use_case = GetUserPlaylistsUseCase(self.playlist_repository)
        
        return self.execute_use_case(
            ensure_favorites_use_case,
            user_id,
            success_message="Favorites playlist ensured",
            then_execute=(get_playlists_use_case, user_id),
            serializer_class=PlaylistResponseSerializer,
        )
    
    def create(self, request):
        """Crea una nueva playlist"""
        user_id = UUID(str(request.user.id))
        
        # Validar datos de entrada
        serializer = PlaylistCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        create_dto = serializer.to_dto(serializer.validated_data)
        create_use_case = CreatePlaylistUseCase(self.playlist_repository)
        
        return self.execute_use_case(
            create_use_case,
            create_dto,
            user_id,
            success_message=f"Playlist '{create_dto.name}' created successfully",
            serializer_class=PlaylistResponseSerializer,
            status_code=status.HTTP_201_CREATED,
        )
    
    def retrieve(self, request, id=None):
        """Obtiene una playlist específica"""
        try:
            playlist_id = UUID(id)
        except (ValueError, TypeError):
            raise Http404("Playlist no encontrada")
        
        # Verificar que la playlist pertenece al usuario
        user_id = UUID(str(request.user.id))
        get_playlists_use_case = GetUserPlaylistsUseCase(self.playlist_repository)
        
        async def get_user_playlist():
            playlists = await get_playlists_use_case.execute(user_id)
            for playlist in playlists:
                if playlist.id == playlist_id:
                    return playlist
            raise Http404("Playlist no encontrada")
        
        return self.execute_use_case(
            lambda: get_user_playlist(),
            success_message="Playlist retrieved successfully",
            serializer_class=PlaylistResponseSerializer,
        )
    
    def update(self, request, id=None):
        """Actualiza una playlist"""
        try:
            playlist_id = UUID(id)
        except (ValueError, TypeError):
            raise Http404("Playlist no encontrada")
        
        # Validar datos de entrada
        serializer = PlaylistUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        update_dto = serializer.to_dto(serializer.validated_data)
        update_use_case = UpdatePlaylistUseCase(self.playlist_repository)
        
        return self.execute_use_case(
            update_use_case,
            {"playlist_id": playlist_id, "update_data": update_dto},
            success_message="Playlist updated successfully",
            serializer_class=PlaylistResponseSerializer,
        )
    
    def destroy(self, request, id=None):
        """Elimina una playlist"""
        try:
            playlist_id = UUID(id)
        except (ValueError, TypeError):
            raise Http404("Playlist no encontrada")
        
        delete_use_case = DeletePlaylistUseCase(self.playlist_repository)
        
        def handle_success(result):
            if result:
                return Response(
                    {"message": "Playlist eliminada exitosamente"},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {"error": "No se pudo eliminar la playlist"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return self.execute_use_case(
            delete_use_case,
            playlist_id,
            success_message="Playlist deleted successfully",
            custom_success_handler=handle_success,
        )
