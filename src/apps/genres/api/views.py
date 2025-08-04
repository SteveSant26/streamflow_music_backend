from typing import Any

from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.genres.api.serializers import GenreSerializer
from apps.genres.infrastructure.models import GenreModel
from common.mixins import LoggingMixin, PaginationMixin
from src.common.utils.schema_decorators import paginated_list_endpoint

from ..api.mappers import GenreMapper
from ..infrastructure.repository import GenreRepository
from ..use_cases import GetAllGenresUseCase, GetGenreUseCase, GetPopularGenresUseCase


@extend_schema_view(
    list=extend_schema(tags=["Genres"]),
    retrieve=extend_schema(tags=["Genres"]),
    popular=extend_schema(tags=["Genres"], description="Get popular genres"),
    search=extend_schema(
        tags=["Genres"],
        description="Search genres by name",
    ),
)
class GenreViewSet(PaginationMixin, viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para consulta de géneros musicales (solo lectura)"""

    queryset = GenreModel.objects.all()
    permission_classes = [AllowAny]
    serializer_class = GenreSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper = GenreMapper()
        self.repository = GenreRepository()

    def get_serializer_class(self) -> Any:
        """Return the serializer class to use for this view"""
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        self.logger.info("Listing genres from local cache")

        get_all_genres = GetAllGenresUseCase(self.repository)
        # Aquí llamamos async desde sync
        genres = async_to_sync(get_all_genres.execute)()

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
        serializer = self.get_serializer(genre_dto)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @paginated_list_endpoint(
        serializer_class=serializer_class,
        tags=["Songs"],
        description="Get random songs from the database",
    )
    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene los géneros más populares de la caché local"""

        get_popular_genres = GetPopularGenresUseCase(self.repository)
        popular_genres = async_to_sync(get_popular_genres.execute)()

        # Convertir entidades a DTOs usando el mapper
        genre_dtos = [self.mapper.entity_to_dto(genre) for genre in popular_genres]
        page = self.paginate_queryset(genre_dtos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        # Si no hay paginación configurada
        serializer = self.get_serializer(genre_dtos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
