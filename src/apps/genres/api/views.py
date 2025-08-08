from typing import Any

from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.genres.api.serializers import GenreSerializer
from apps.genres.infrastructure.filters import GenreModelFilter
from apps.genres.infrastructure.models import GenreModel
from common.mixins import FilteredViewSetMixin
from common.utils.schema_decorators import paginated_list_endpoint

from ..api.mappers import GenreMapper
from ..infrastructure.repository import GenreRepository
from ..use_cases import GetAllGenresUseCase, GetGenreUseCase, GetPopularGenresUseCase


@extend_schema_view(
    list=extend_schema(tags=["Genres"], description="List all genres from local cache"),
    retrieve=extend_schema(tags=["Genres"], description="Get a specific genre by ID"),
    popular=extend_schema(tags=["Genres"], description="Get popular genres"),
)
class GenreViewSet(FilteredViewSetMixin):
    """ViewSet para consulta de géneros musicales (solo lectura) con filtros integrados"""

    queryset = GenreModel.objects.all()
    filterset_class = GenreModelFilter

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper = GenreMapper()
        self.repository = GenreRepository()
        # Use cases
        self.get_all_genres = GetAllGenresUseCase(self.repository)
        self.get_genre = GetGenreUseCase(self.repository)
        self.get_popular_genres = GetPopularGenresUseCase(self.repository)

    def get_serializer_class(self) -> Any:
        return GenreSerializer

    @paginated_list_endpoint(
        serializer_class=GenreSerializer,
        tags=["Genres"],
        description="Get popular genres from the database",
    )
    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene los géneros más populares"""
        popular_genres = async_to_sync(self.get_popular_genres.execute)()
        genre_dtos = [self.mapper.entity_to_dto(genre) for genre in popular_genres]

        page = self.paginate_queryset(genre_dtos)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(genre_dtos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
