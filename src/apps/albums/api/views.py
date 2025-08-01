from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.albums.api.serializers import AlbumResponseSerializer
from apps.albums.infrastructure.models.album_model import AlbumModel
from common.mixins.logging_mixin import LoggingMixin

from ..infrastructure.repository import AlbumRepository
from ..use_cases import (
    GetAlbumsByArtistUseCase,
    GetAlbumUseCase,
    GetAllAlbumsUseCase,
    GetPopularAlbumsUseCase,
    SearchAlbumsByTitleUseCase,
)

# Instancia global del repositorio (idealmente esto debería ser inyección de dependencias)
album_repository = AlbumRepository()


@extend_schema_view(
    list=extend_schema(tags=["Albums"]),
    retrieve=extend_schema(tags=["Albums"]),
    popular=extend_schema(tags=["Albums"], description="Get popular albums"),
    search=extend_schema(tags=["Albums"], description="Search albums by title"),
    by_artist=extend_schema(tags=["Albums"], description="Get albums by artist"),
)
class AlbumViewSet(viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para gestión de álbumes (solo lectura)"""

    queryset = AlbumModel.objects.all()
    serializer_class = AlbumResponseSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Define permisos según la acción"""
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """Obtiene todos los álbumes"""
        self.logger.info("Getting all albums")

        get_all_albums = GetAllAlbumsUseCase(album_repository)
        albums = get_all_albums.execute()

        return Response(
            self.get_serializer(albums, many=True).data, status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Obtiene un álbum específico"""
        self.logger.info(f"Getting album with ID: {pk}")

        get_album = GetAlbumUseCase(album_repository)
        album = get_album.execute(pk)

        return Response(self.get_serializer(album).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene álbumes populares"""
        limit = int(request.query_params.get("limit", 10))
        self.logger.info(f"Getting popular albums with limit: {limit}")

        get_popular_albums = GetPopularAlbumsUseCase(album_repository)
        albums = get_popular_albums.execute(limit)

        return Response(
            self.get_serializer(albums, many=True).data, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Busca álbumes por título"""
        title = request.query_params.get("title", "")
        limit = int(request.query_params.get("limit", 10))

        if not title:
            return Response(
                {"error": "El parámetro 'title' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Searching albums by title: {title}")

        search_albums = SearchAlbumsByTitleUseCase(album_repository)
        albums = search_albums.execute(title, limit)

        return Response(
            self.get_serializer(albums, many=True).data, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="by-artist")
    def by_artist(self, request):
        """Obtiene álbumes por artista"""
        artist_id = request.query_params.get("artist_id", "")
        limit = int(request.query_params.get("limit", 10))

        if not artist_id:
            return Response(
                {"error": "El parámetro 'artist_id' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Getting albums by artist: {artist_id}")

        get_albums_by_artist = GetAlbumsByArtistUseCase(album_repository)
        albums = get_albums_by_artist.execute(artist_id, limit)

        return Response(
            self.get_serializer(albums, many=True).data, status=status.HTTP_200_OK
        )
