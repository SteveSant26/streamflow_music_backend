<<<<<<< HEAD
from asgiref.sync import async_to_sync
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
=======
from drf_spectacular.utils import extend_schema, extend_schema_view
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from rest_framework.permissions import AllowAny

from apps.albums.api.serializers import AlbumResponseSerializer
<<<<<<< HEAD
=======
from apps.albums.infrastructure.filters import AlbumModelFilter
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from apps.albums.infrastructure.models.album_model import AlbumModel
from common.mixins import FilteredViewSetMixin

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
<<<<<<< HEAD
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
=======
    list=extend_schema(
        tags=["Albums"],
        description="""
        List all albums with optional filtering.

        **Available Filters:**
        - `title`: Search by title (contains)
        - `artist_name`: Search by artist name (contains)
        - `artist_id`: Filter by specific artist ID
        - `source_type`: Source type (manual, youtube, spotify, etc.)
        - `min_release_date`/`max_release_date`: Release date range
        - `release_year`: Specific release year
        - `min_total_tracks`/`max_total_tracks`: Track count range
        - `min_play_count`/`max_play_count`: Play count range
        - `has_cover_image`: Only albums with cover image
        - `has_description`: Only albums with description
        - `created_after`/`created_before`: Creation date range
        - `popular`: Only popular albums (>1000 plays)
        - `recent`: Only recently added albums
        - `search`: General search in title, artist, and description

        **Ordering:**
        Use `ordering` parameter with: title, release_date, total_tracks, play_count,
        created_at, updated_at, artist__name, artist__followers_count
        """,
        summary="Get albums list",
    ),
    retrieve=extend_schema(
        tags=["Albums"],
        description="Get a specific album by ID",
        summary="Get album details",
    ),
)
class AlbumViewSet(FilteredViewSetMixin):
    """ViewSet para gestión de álbumes (solo lectura) con filtros integrados"""

    queryset = AlbumModel.objects.select_related("artist").all().order_by("-created_at")
    filterset_class = AlbumModelFilter

    permission_classes = [AllowAny]

    def get_serializer_class(self):
        return AlbumResponseSerializer

    # Campos por los que se puede ordenar
    ordering_fields = [
        "title",
        "release_date",
        "total_tracks",
        "play_count",
        "created_at",
        "updated_at",
        "artist__name",
        "artist__followers_count",
    ]
    ordering = ["-created_at"]
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

    # Búsqueda simple
    search_fields = ["title", "description", "artist__name"]

<<<<<<< HEAD
    def retrieve(self, request, pk=None, *args, **kwargs):
        """Obtiene un álbum específico"""
        self.logger.info(f"Getting album with ID: {pk}")

        get_album = GetAlbumUseCase(album_repository)
        album = async_to_sync(get_album.execute)(pk)

        # Convertir entidad a DTO usando el mapper
        album_dto = self.mapper.entity_to_dto(album)
        serializer = self.get_serializer(album_dto)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "limit",
                OpenApiTypes.INT,
                description="Number of popular albums to return",
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene álbumes populares"""
        limit = int(request.query_params.get("limit", 10))
        self.logger.info(f"Getting popular albums with limit: {limit}")

        request_dto = GetPopularAlbumsRequestDTO(limit=limit)
        get_popular_albums = GetPopularAlbumsUseCase(album_repository)
        albums = async_to_sync(get_popular_albums.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        album_dtos = [self.mapper.entity_to_dto(album) for album in albums]
        serializer = self.get_serializer(album_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "title",
                OpenApiTypes.STR,
                description="Album title to search for",
                required=True,
            ),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Number of results to return"
            ),
        ],
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

        request_dto = SearchAlbumsByTitleRequestDTO(title=title, limit=limit)
        search_albums = SearchAlbumsByTitleUseCase(album_repository)
        albums = async_to_sync(search_albums.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        album_dtos = [self.mapper.entity_to_dto(album) for album in albums]
        serializer = self.get_serializer(album_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "artist_id",
                OpenApiTypes.STR,
                description="Artist ID to filter albums",
                required=True,
            ),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Number of results to return"
            ),
        ],
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

        request_dto = GetAlbumsByArtistRequestDTO(artist_id=artist_id, limit=limit)
        get_albums_by_artist = GetAlbumsByArtistUseCase(album_repository)
        albums = async_to_sync(get_albums_by_artist.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        album_dtos = [self.mapper.entity_to_dto(album) for album in albums]
        serializer = self.get_serializer(album_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
=======
    def get_queryset(self):
        """
        Personalizar el queryset base con optimizaciones
        """
        queryset = super().get_queryset()

        # Optimizar consultas incluyendo datos relacionados
        queryset = queryset.select_related("artist")

        return queryset
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
