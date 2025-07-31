from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.artists.api.serializers import ArtistResponseSerializer
from apps.artists.infrastructure.models import ArtistModel
from common.mixins.logging_mixin import LoggingMixin

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
class ArtistViewSet(viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para gestión de artistas (solo lectura)"""

    queryset = ArtistModel.objects.all()
    serializer_class = ArtistResponseSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        """Define permisos según la acción"""
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """Obtiene todos los artistas"""
        self.logger.info("Getting all artists")

        get_all_artists = GetAllArtistsUseCase(artist_repository)
        artists = get_all_artists.execute()

        return Response(
            self.get_serializer(artists, many=True).data, status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Obtiene un artista específico"""
        self.logger.info(f"Getting artist with ID: {pk}")

        get_artist = GetArtistUseCase(artist_repository)
        artist = get_artist.execute(pk)

        return Response(self.get_serializer(artist).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene artistas populares"""
        limit = int(request.query_params.get("limit", 10))
        self.logger.info(f"Getting popular artists with limit: {limit}")

        get_popular_artists = GetPopularArtistsUseCase(artist_repository)
        artists = get_popular_artists.execute(limit)

        return Response(
            self.get_serializer(artists, many=True).data, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"], url_path="verified")
    def verified(self, request):
        """Obtiene artistas verificados"""
        limit = int(request.query_params.get("limit", 10))
        self.logger.info(f"Getting verified artists with limit: {limit}")

        get_verified_artists = GetVerifiedArtistsUseCase(artist_repository)
        artists = get_verified_artists.execute(limit)

        return Response(
            self.get_serializer(artists, many=True).data, status=status.HTTP_200_OK
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

        search_artists = SearchArtistsByNameUseCase(artist_repository)
        artists = search_artists.execute(name, limit)

        return Response(
            self.get_serializer(artists, many=True).data, status=status.HTTP_200_OK
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

        get_artists_by_country = GetArtistsByCountryUseCase(artist_repository)
        artists = get_artists_by_country.execute(country, limit)

        return Response(
            self.get_serializer(artists, many=True).data, status=status.HTTP_200_OK
        )
