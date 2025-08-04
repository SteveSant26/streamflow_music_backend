from asgiref.sync import async_to_sync
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.artists.api.serializers import ArtistResponseSerializer
from apps.artists.infrastructure.filters import ArtistModelFilter
from apps.artists.infrastructure.models import ArtistModel
from common.mixins.logging_mixin import LoggingMixin
from src.common.mixins.pagination_mixin import PaginationMixin
from src.common.utils.schema_decorators import paginated_list_endpoint

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


@extend_schema_view(
    list=extend_schema(tags=["Artists"]),
    retrieve=extend_schema(tags=["Artists"]),
    popular=extend_schema(tags=["Artists"], description="Get popular artists"),
    verified=extend_schema(tags=["Artists"], description="Get verified artists"),
    search=extend_schema(tags=["Artists"], description="Search artists by name"),
    by_country=extend_schema(tags=["Artists"], description="Get artists by country"),
)
class ArtistViewSet(PaginationMixin, viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para gestión de artistas (solo lectura)"""

    queryset = ArtistModel.objects.all()
    serializer_class = ArtistResponseSerializer
    permission_classes = [AllowAny]
    filterset_class = ArtistModelFilter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper = ArtistMapper()

    def get_permissions(self):
        """Define permisos según la acción"""
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """Obtiene todos los artistas"""
        self.logger.info("Getting all artists")

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

    @paginated_list_endpoint(
        serializer_class=serializer_class,
        tags=["Artists"],
        description="Get popular artists from the database",
    )
    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene artistas populares"""
        limit = self.paginator.page_size
        self.logger.info(f"Getting popular artists with limit: {limit}")

        request_dto = GetPopularArtistsRequestDTO(limit=limit)
        get_popular_artists = GetPopularArtistsUseCase(artist_repository)
        artists = async_to_sync(get_popular_artists.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        artist_dtos = [self.mapper.entity_to_dto(artist) for artist in artists]
        serializer = self.get_serializer(artist_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @paginated_list_endpoint(
        serializer_class=serializer_class,
        tags=["Artists"],
        description="Get verified artists from the database",
    )
    @action(detail=False, methods=["get"], url_path="verified")
    def verified(self, request):
        """Obtiene artistas verificados"""
        limit = self.paginator.page_size
        self.logger.info(f"Getting verified artists with limit: {limit}")

        request_dto = GetVerifiedArtistsRequestDTO(limit=limit)
        get_verified_artists = GetVerifiedArtistsUseCase(artist_repository)
        artists = async_to_sync(get_verified_artists.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        artist_dtos = [self.mapper.entity_to_dto(artist) for artist in artists]
        serializer = self.get_serializer(artist_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @paginated_list_endpoint(
        serializer_class=serializer_class,
        tags=["Artists"],
        description="Get popular artists from the database",
        parameters=[
            OpenApiParameter(
                "name",
                OpenApiTypes.STR,
                description="Search term for artists",
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Busca artistas por nombre"""
        name = request.query_params.get("name", "")
        limit = self.paginator.page_size

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

    @paginated_list_endpoint(
        serializer_class=serializer_class,
        tags=["Artists"],
        description="Get popular artists from the database",
        parameters=[
            OpenApiParameter(
                "country",
                OpenApiTypes.STR,
                description="Country to filter artists",
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="by-country")
    def by_country(self, request):
        """Obtiene artistas por país"""
        country = request.query_params.get("country", "")
        limit = self.paginator.page_size

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
