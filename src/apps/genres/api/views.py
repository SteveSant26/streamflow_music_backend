from asgiref.sync import async_to_sync
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.genres.api.serializers import GenreSerializer
from apps.genres.infrastructure.models.genre_model import GenreModel
from common.mixins.logging_mixin import LoggingMixin

from ..api.dtos import GetPopularGenresRequestDTO, SearchGenresByNameRequestDTO
from ..api.mappers import GenreMapper
from ..infrastructure.repository import GenreRepository
from ..use_cases import (
    GetAllGenresUseCase,
    GetGenreUseCase,
    GetPopularGenresUseCase,
    SearchGenresByNameUseCase,
)


@extend_schema_view(
    list=extend_schema(tags=["Genres"]),
    retrieve=extend_schema(tags=["Genres"]),
    popular=extend_schema(tags=["Genres"], description="Get popular genres"),
    search=extend_schema(
        tags=["Genres"],
        description="Search genres by name",
    ),
)
class GenreViewSet(viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para consulta de géneros musicales (solo lectura)"""

    queryset = GenreModel.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper = GenreMapper()
        self.repository = GenreRepository()

    def list(self, request, *args, **kwargs):
        """Lista todos los géneros disponibles localmente"""
        self.logger.info("Listing genres from local cache")

        get_all_genres = GetAllGenresUseCase(self.repository)
        genres = async_to_sync(get_all_genres.execute)()

        # Convertir entidades a DTOs usando el mapper
        genre_dtos = [self.mapper.entity_to_dto(genre) for genre in genres]
        serializer = GenreSerializer(genre_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Obtiene un género específico"""
        self.logger.info(f"Retrieving genre {pk}")

        get_genre = GetGenreUseCase(self.repository)
        genre = async_to_sync(get_genre.execute)(pk)

        # Convertir entidad a DTO usando el mapper
        genre_dto = self.mapper.entity_to_dto(genre)
        serializer = GenreSerializer(genre_dto)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "limit",
                OpenApiTypes.INT,
                description="Number of popular genres to return",
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene los géneros más populares de la caché local"""
        limit = int(request.query_params.get("limit", 10))
        self.logger.info(f"Getting popular genres with limit: {limit}")

        request_dto = GetPopularGenresRequestDTO(limit=limit)
        get_popular_genres = GetPopularGenresUseCase(self.repository)
        popular_genres = async_to_sync(get_popular_genres.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        genre_dtos = [self.mapper.entity_to_dto(genre) for genre in popular_genres]
        serializer = GenreSerializer(genre_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "q",
                OpenApiTypes.STR,
                description="Search query for genres",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Busca géneros por nombre"""
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Searching genres for: {query}")

        request_dto = SearchGenresByNameRequestDTO(query=query, limit=10)
        search_genres = SearchGenresByNameUseCase(self.repository)
        matching_genres = async_to_sync(search_genres.execute)(request_dto)

        # Convertir entidades a DTOs usando el mapper
        genre_dtos = [self.mapper.entity_to_dto(genre) for genre in matching_genres]
        serializer = GenreSerializer(genre_dtos, many=True)

        return Response(
            {
                "query": query,
                "results": serializer.data,
                "total": len(matching_genres),
            },
            status=status.HTTP_200_OK,
        )
