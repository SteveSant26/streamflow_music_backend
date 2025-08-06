from asgiref.sync import async_to_sync
from django.http import Http404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.playlists.api.dtos import (
    AddSongToPlaylistRequestDTO,
    RemoveSongFromPlaylistRequestDTO,
)
from apps.playlists.api.mappers import PlaylistSongEntityDTOMapper
from apps.playlists.api.serializers import (
    AddSongToPlaylistSerializer,
    PlaylistSongResponseSerializer,
)
from apps.playlists.infrastructure.models.playlist_model import PlaylistModel
from apps.playlists.infrastructure.repository import PlaylistRepository
from apps.playlists.use_cases import (
    AddSongToPlaylistUseCase,
    GetPlaylistSongsUseCase,
    RemoveSongFromPlaylistUseCase,
)
from apps.songs.infrastructure.repository.song_repository import SongRepository
from common.mixins import SimpleViewSetMixin


@extend_schema_view(
    list_songs=extend_schema(
        tags=["Playlist Songs"],
        description="Lista las canciones de una playlist específica",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="ID de la playlist",
            )
        ],
    ),
    add_song=extend_schema(
        tags=["Playlist Songs"],
        description="Añade una canción a una playlist",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="ID de la playlist",
            )
        ],
    ),
    remove_song=extend_schema(
        tags=["Playlist Songs"],
        description="Remueve una canción de una playlist",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="ID de la playlist",
            ),
            OpenApiParameter(
                name="song_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="ID de la canción",
            ),
        ],
    ),
)
class PlaylistSongViewSet(SimpleViewSetMixin):
    """ViewSet para gestionar canciones en playlists"""

    # Atributos requeridos para DRF y drf-spectacular
    queryset = PlaylistModel.objects.all()
    serializer_class = PlaylistSongResponseSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.playlist_repository = PlaylistRepository()
        self.song_repository = SongRepository()
        self.mapper = PlaylistSongEntityDTOMapper()

    def get_serializer_class(self):
        """Selecciona el serializer según la acción"""
        action_to_serializer = {
            "list_songs": PlaylistSongResponseSerializer,
            "add_song": AddSongToPlaylistSerializer,
            "remove_song": None,  # No necesita serializer para DELETE
        }
        return action_to_serializer.get(self.action, PlaylistSongResponseSerializer)

    def get_queryset(self):
        """Retorna el queryset base"""
        return PlaylistModel.objects.all()

    @extend_schema(
        responses={200: PlaylistSongResponseSerializer(many=True)},
        description="Lista las canciones de una playlist específica",
    )
    @action(detail=True, methods=["get"], url_path="songs")
    def list_songs(self, request, pk=None):
        """Lista las canciones de una playlist"""
        self.log_action("list_songs", f"playlist_id={pk}")

        if not pk:
            raise Http404("Playlist no encontrada")

        try:
            playlist_id = str(pk)

            # Ejecutar caso de uso
            get_songs_use_case = GetPlaylistSongsUseCase(self.playlist_repository)
            playlist_songs = async_to_sync(get_songs_use_case.execute)(playlist_id)

            # Convertir entidades a DTOs
            song_dtos = self.mapper.entities_to_dtos(playlist_songs)

            # Serializar respuesta
            serializer = PlaylistSongResponseSerializer(song_dtos, many=True)

            self.logger.info(
                f"Retrieved {len(playlist_songs)} songs for playlist {playlist_id}"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            self.logger.error(f"Error listing playlist songs: {str(e)}")
            return Response(
                {"error": "Error obteniendo canciones de la playlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        request=AddSongToPlaylistSerializer,
        responses={201: PlaylistSongResponseSerializer},
        description="Agrega una canción a la playlist",
    )
    @action(detail=True, methods=["post"], url_path="songs")
    def add_song(self, request, pk=None):
        """Agrega una canción a la playlist"""
        self.log_action("add_song", f"playlist_id={pk}")

        if not pk:
            raise Http404("Playlist no encontrada")

        try:
            playlist_id = str(pk)

            # Validar datos de entrada
            serializer = AddSongToPlaylistSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Una vez validado, accedemos a los datos originales que ya están validados
            song_id = request.data.get("song_id")
            position = request.data.get("position")

            if not song_id:
                return Response(
                    {"error": "song_id es requerido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Crear DTO
            add_dto = AddSongToPlaylistRequestDTO(
                playlist_id=playlist_id,
                song_id=str(song_id),
                position=position,
            )

            # Ejecutar caso de uso
            add_song_use_case = AddSongToPlaylistUseCase(self.playlist_repository)
            playlist_song = async_to_sync(add_song_use_case.execute)(add_dto)

            # Convertir entidad a DTO y serializar
            song_dto = self.mapper.entity_to_dto(playlist_song)
            response_serializer = PlaylistSongResponseSerializer(song_dto)

            self.logger.info(f"Song {add_dto.song_id} added to playlist {playlist_id}")
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            self.logger.error(f"Error adding song to playlist: {str(e)}")
            return Response(
                {"error": "Error añadiendo canción a la playlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        responses={204: None}, description="Remueve una canción de la playlist"
    )
    @action(detail=True, methods=["delete"], url_path="songs/(?P<song_id>[^/.]+)")
    def remove_song(self, request, pk=None, song_id=None):
        """Remueve una canción de la playlist"""
        self.log_action("remove_song", f"playlist_id={pk}, song_id={song_id}")

        if not pk or not song_id:
            raise Http404("Playlist o canción no encontrada")

        try:
            playlist_id = str(pk)
            song_id = str(song_id)

            # Crear DTO
            remove_dto = RemoveSongFromPlaylistRequestDTO(
                playlist_id=playlist_id,
                song_id=song_id,
            )

            # Ejecutar caso de uso
            remove_song_use_case = RemoveSongFromPlaylistUseCase(
                self.playlist_repository
            )
            result = async_to_sync(remove_song_use_case.execute)(remove_dto)

            if result:
                self.logger.info(f"Song {song_id} removed from playlist {playlist_id}")
                return Response(
                    {"message": "Canción removida de la playlist exitosamente"},
                    status=status.HTTP_204_NO_CONTENT,
                )
            else:
                return Response(
                    {"error": "No se pudo remover la canción de la playlist"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            self.logger.error(f"Error removing song from playlist: {str(e)}")
            return Response(
                {"error": "Error removiendo canción de la playlist"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
