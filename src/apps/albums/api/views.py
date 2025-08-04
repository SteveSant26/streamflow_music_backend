from asgiref.sync import async_to_sync
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.albums.api.serializers import AlbumResponseSerializer
from apps.albums.infrastructure.filters import AlbumModelFilter
from apps.albums.infrastructure.models.album_model import AlbumModel
from common.mixins.logging_mixin import LoggingMixin
from src.common.mixins.pagination_mixin import PaginationMixin
from src.common.utils.schema_decorators import paginated_list_endpoint

from ..api.dtos import (
    GetAlbumsByArtistRequestDTO,
    GetPopularAlbumsRequestDTO,
    SearchAlbumsByTitleRequestDTO,
)
from ..api.mappers import AlbumMapper
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
class AlbumViewSet(PaginationMixin, viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para gestión de álbumes (solo lectura)"""

    queryset = AlbumModel.objects.select_related("artist").all()
    serializer_class = AlbumResponseSerializer
    permission_classes = [AllowAny]
    filterset_class = AlbumModelFilter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper = AlbumMapper()

    def get_permissions(self):
        """Define permisos según la acción"""
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """Obtiene todos los álbumes"""
        self.logger.info("Getting all albums")

        get_all_albums = GetAllAlbumsUseCase(album_repository)
        albums = async_to_sync(get_all_albums.execute)()

        # Convertir entidades a DTOs usando el mapper
        album_dtos = [self.mapper.entity_to_dto(album) for album in albums]
        serializer = self.get_serializer(album_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Obtiene un álbum específico"""
        self.logger.info(f"Getting album with ID: {pk}")

        get_album = GetAlbumUseCase(album_repository)
        album = async_to_sync(get_album.execute)(pk)

        # Convertir entidad a DTO usando el mapper
        album_dto = self.mapper.entity_to_dto(album)
        serializer = self.get_serializer(album_dto)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @paginated_list_endpoint(
        serializer_class=serializer_class,
        tags=["Albums"],
        description="Get popularalbums from the database",
    )
    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene álbumes populares"""
        limit = self.paginator.page_size
        self.logger.info(f"Getting popular albums with limit: {limit}")

        request_dto = GetPopularAlbumsRequestDTO(limit=limit)
        get_popular_albums = GetPopularAlbumsUseCase(album_repository)
        albums = async_to_sync(get_popular_albums.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        album_dtos = [self.mapper.entity_to_dto(album) for album in albums]
        serializer = self.get_serializer(album_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @paginated_list_endpoint(
        serializer_class=serializer_class,
        tags=["Albums"],
        description="Get popular albums from the database",
        parameters=[
            OpenApiParameter(
                "title",
                OpenApiTypes.STR,
                description="Search term for popular albums",
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Busca álbumes por título"""
        title = request.query_params.get("title", "")
        limit = self.paginator.page_size

        if not title:
            return Response(
                {"error": "El parámetro 'title' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Searching albums by title: {title}")

        request_dto = SearchAlbumsByTitleRequestDTO(title=title, limit=limit)
        search_albums = SearchAlbumsByTitleUseCase(album_repository)
        albums = async_to_sync(search_albums.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        album_dtos = [self.mapper.entity_to_dto(album) for album in albums]
        serializer = self.get_serializer(album_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @paginated_list_endpoint(
        serializer_class=serializer_class,
        tags=["Albums"],
        description="Get popular albums from the database",
        parameters=[
            OpenApiParameter(
                "artist_id",
                OpenApiTypes.STR,
                description="Artist ID to filter albums",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="by-artist")
    def by_artist(self, request):
        """Obtiene álbumes por artista"""
        artist_id = request.query_params.get("artist_id", "")
        limit = self.paginator.page_size

        if not artist_id:
            return Response(
                {"error": "El parámetro 'artist_id' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Getting albums by artist: {artist_id}")

        request_dto = GetAlbumsByArtistRequestDTO(artist_id=artist_id, limit=limit)
        get_albums_by_artist = GetAlbumsByArtistUseCase(album_repository)
        albums = async_to_sync(get_albums_by_artist.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        album_dtos = [self.mapper.entity_to_dto(album) for album in albums]
        serializer = self.get_serializer(album_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
