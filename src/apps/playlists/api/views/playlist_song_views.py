from uuid import UUID

from django.http import Http404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.playlists.api.serializers import (
    AddSongToPlaylistSerializer,
    PlaylistSongResponseSerializer,
)
from apps.playlists.infrastructure.repository import PlaylistRepository
from apps.playlists.use_cases import (
    AddSongToPlaylistUseCase,
    GetPlaylistSongsUseCase,
    RemoveSongFromPlaylistUseCase,
)
from apps.songs.infrastructure.repository import SongRepository
from common.mixins.use_case_api_view_mixin import UseCaseAPIViewMixin


class PlaylistSongViewSet(GenericViewSet, UseCaseAPIViewMixin):
    """ViewSet para gestionar canciones en playlists"""
    
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist_repository = PlaylistRepository()
        self.song_repository = SongRepository()
    
    @action(detail=True, methods=['get'], url_path='songs')
    def list_songs(self, request, pk=None):
        """Lista las canciones de una playlist"""
        try:
            playlist_id = UUID(pk)
        except (ValueError, TypeError):
            raise Http404("Playlist no encontrada")
        
        get_songs_use_case = GetPlaylistSongsUseCase(
            self.playlist_repository,
            self.song_repository
        )
        
        return self.execute_use_case(
            get_songs_use_case,
            playlist_id,
            success_message="Playlist songs retrieved successfully",
            serializer_class=PlaylistSongResponseSerializer,
            many=True,
        )
    
    @action(detail=True, methods=['post'], url_path='songs')
    def add_song(self, request, pk=None):
        """Agrega una canción a la playlist"""
        try:
            playlist_id = UUID(pk)
        except (ValueError, TypeError):
            raise Http404("Playlist no encontrada")
        
        # Validar datos de entrada
        serializer = AddSongToPlaylistSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        add_dto = serializer.to_dto(serializer.validated_data)
        add_song_use_case = AddSongToPlaylistUseCase(self.playlist_repository)
        
        request_data = {
            "playlist_id": playlist_id,
            "song_id": add_dto.song_id,
            "position": add_dto.position,
        }
        
        return self.execute_use_case(
            add_song_use_case,
            request_data,
            success_message="Song added to playlist successfully",
            status_code=status.HTTP_201_CREATED,
        )
    
    @action(detail=True, methods=['delete'], url_path='songs/(?P<song_id>[^/.]+)')
    def remove_song(self, request, pk=None, song_id=None):
        """Remueve una canción de la playlist"""
        try:
            playlist_id = UUID(pk)
            song_uuid = UUID(song_id)
        except (ValueError, TypeError):
            raise Http404("Playlist o canción no encontrada")
        
        remove_song_use_case = RemoveSongFromPlaylistUseCase(self.playlist_repository)
        
        request_data = {
            "playlist_id": playlist_id,
            "song_id": song_uuid,
        }
        
        def handle_success(result):
            if result:
                return Response(
                    {"message": "Canción removida de la playlist exitosamente"},
                    status=status.HTTP_204_NO_CONTENT
                )
            else:
                return Response(
                    {"error": "No se pudo remover la canción de la playlist"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return self.execute_use_case(
            remove_song_use_case,
            request_data,
            success_message="Song removed from playlist successfully",
            custom_success_handler=handle_success,
        )
