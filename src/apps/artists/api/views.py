<<<<<<< HEAD
from asgiref.sync import async_to_sync
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
=======
from typing import Any

from drf_spectacular.utils import extend_schema, extend_schema_view
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

from apps.artists.api.serializers import ArtistResponseSerializer
from apps.artists.infrastructure.filters import ArtistModelFilter
from apps.artists.infrastructure.models import ArtistModel
<<<<<<< HEAD
from common.mixins.logging_mixin import LoggingMixin

from ..api.dtos import (
    GetArtistsByCountryRequestDTO,
    GetPopularArtistsRequestDTO,
    GetVerifiedArtistsRequestDTO,
    SearchArtistsByNameRequestDTO,
)
from ..api.mappers import ArtistMapper
from ..infrastructure.repository import ArtistRepository
from ..use_cases import (
    GetAllArtistsUseCase,
    GetArtistsByCountryUseCase,
    GetArtistUseCase,
    GetPopularArtistsUseCase,
    GetVerifiedArtistsUseCase,
    SearchArtistsByNameUseCase,
)

# Instancia global del repositorio (idealmente esto debería ser inyección de dependencias)
artist_repository = ArtistRepository()
=======
from common.mixins import FilteredViewSetMixin
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33


@extend_schema_view(
    list=extend_schema(
        tags=["Artists"],
        description="""
        List all artists with optional filtering.

        **Available Filters:**
        - `name`: Search by name (contains)
        - `country`: Filter by exact country
        - `is_verified`: Only verified artists
        - `min_followers_count`/`max_followers_count`: Followers count range
        - `popular`: Only popular artists (>1000 followers)
        - `verified`: Only verified artists
        - `recent`: Only recently added artists
        - `search`: General search in name, biography, and country
        - `has_biography`: Only artists with biography
        - `has_image`: Only artists with image
        - `created_after`/`created_before`: Creation date range
        - `source_type`: Source type (manual, youtube, spotify, etc.)

        **Ordering:**
        Use `ordering` parameter with: name, followers_count, created_at, updated_at
        """,
        summary="Get artists list",
    ),
    retrieve=extend_schema(
        tags=["Artists"],
        description="Get a specific artist by ID",
        summary="Get artist details",
    ),
)
class ArtistViewSet(FilteredViewSetMixin):
    """ViewSet para gestión de artistas (solo lectura) con filtros integrados"""

    queryset = ArtistModel.objects.all().order_by("-created_at")
    filterset_class = ArtistModelFilter

<<<<<<< HEAD
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper = ArtistMapper()

    def get_permissions(self):
        """Define permisos según la acción"""
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
=======
    def get_serializer_class(self) -> Any:
        return ArtistResponseSerializer
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

    # Campos por los que se puede ordenar
    ordering_fields = ["name", "followers_count", "created_at", "updated_at"]
    ordering = ["-created_at"]  # Ordenamiento por defecto

<<<<<<< HEAD
        get_all_artists = GetAllArtistsUseCase(artist_repository)
        artists = async_to_sync(get_all_artists.execute)()

        # Convertir entidades a DTOs usando el mapper
        artist_dtos = [self.mapper.entity_to_dto(artist) for artist in artists]
        serializer = self.get_serializer(artist_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Obtiene un artista específico"""
        self.logger.info(f"Getting artist with ID: {pk}")

        get_artist = GetArtistUseCase(artist_repository)
        artist = async_to_sync(get_artist.execute)(pk)

        # Convertir entidad a DTO usando el mapper
        artist_dto = self.mapper.entity_to_dto(artist)
        serializer = self.get_serializer(artist_dto)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "limit",
                OpenApiTypes.INT,
                description="Number of popular artists to return",
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene artistas populares"""
        limit = int(request.query_params.get("limit", 10))
        self.logger.info(f"Getting popular artists with limit: {limit}")

        request_dto = GetPopularArtistsRequestDTO(limit=limit)
        get_popular_artists = GetPopularArtistsUseCase(artist_repository)
        artists = async_to_sync(get_popular_artists.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        artist_dtos = [self.mapper.entity_to_dto(artist) for artist in artists]
        serializer = self.get_serializer(artist_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "limit",
                OpenApiTypes.INT,
                description="Number of verified artists to return",
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="verified")
    def verified(self, request):
        """Obtiene artistas verificados"""
        limit = int(request.query_params.get("limit", 10))
        self.logger.info(f"Getting verified artists with limit: {limit}")

        request_dto = GetVerifiedArtistsRequestDTO(limit=limit)
        get_verified_artists = GetVerifiedArtistsUseCase(artist_repository)
        artists = async_to_sync(get_verified_artists.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        artist_dtos = [self.mapper.entity_to_dto(artist) for artist in artists]
        serializer = self.get_serializer(artist_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                OpenApiTypes.STR,
                description="Artist name to search for",
                required=True,
            ),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Number of results to return"
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Busca artistas por nombre"""
        name = request.query_params.get("name", "")
        limit = int(request.query_params.get("limit", 10))

        if not name:
            return Response(
                {"error": "El parámetro 'name' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Searching artists by name: {name}")

        request_dto = SearchArtistsByNameRequestDTO(name=name, limit=limit)
        search_artists = SearchArtistsByNameUseCase(artist_repository)
        artists = async_to_sync(search_artists.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        artist_dtos = [self.mapper.entity_to_dto(artist) for artist in artists]
        serializer = self.get_serializer(artist_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "country",
                OpenApiTypes.STR,
                description="Country to filter artists",
                required=True,
            ),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Number of results to return"
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="by-country")
    def by_country(self, request):
        """Obtiene artistas por país"""
        country = request.query_params.get("country", "")
        limit = int(request.query_params.get("limit", 10))

        if not country:
            return Response(
                {"error": "El parámetro 'country' es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Getting artists by country: {country}")

        request_dto = GetArtistsByCountryRequestDTO(country=country, limit=limit)
        get_artists_by_country = GetArtistsByCountryUseCase(artist_repository)
        artists = async_to_sync(get_artists_by_country.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        artist_dtos = [self.mapper.entity_to_dto(artist) for artist in artists]
        serializer = self.get_serializer(artist_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
=======
    # Búsqueda simple
    search_fields = [
        "name",
        "biography",
    ]
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
