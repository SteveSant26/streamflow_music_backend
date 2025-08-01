from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.genres.api.serializers import GenreSerializer
from apps.genres.infrastructure.models.genre_model import GenreModel
from common.mixins.logging_mixin import LoggingMixin

from ..api.mappers import GenreMapper


@extend_schema_view(
    list=extend_schema(tags=["Genres"]),
    retrieve=extend_schema(tags=["Genres"]),
    popular=extend_schema(tags=["Genres"], description="Get popular genres"),
    search=extend_schema(
        tags=["Genres"],
        description="Search genres (checks YouTube if not found locally)",
    ),
)
class GenreViewSet(viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para consulta de géneros musicales (solo lectura, datos de YouTube)"""

    queryset = GenreModel.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [AllowAny]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mapper = GenreMapper()

    def list(self, request, *args, **kwargs):
        """Lista todos los géneros disponibles localmente"""
        self.logger.info("Listing genres from local cache")

        queryset = self.get_queryset().filter(is_active=True)

        # Convertir entidades a DTOs usando el mapper
        genre_dtos = [self.mapper.entity_to_response_dto(genre) for genre in queryset]
        serializer = GenreSerializer(genre_dtos, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Obtiene un género específico"""
        genre = self.get_object()
        self.logger.info(f"Retrieving genre {genre.id}")

        # Convertir entidad a DTO usando el mapper
        genre_dto = self.mapper.entity_to_response_dto(genre)
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
        self.logger.info("Getting popular genres")

        popular_genres = (
            self.get_queryset()
            .filter(is_active=True)
            .order_by("-popularity_score")[:10]
        )

        # Convertir entidades a DTOs usando el mapper
        genre_dtos = [
            self.mapper.entity_to_response_dto(genre) for genre in popular_genres
        ]
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

        # Los géneros musicales son más estáticos, buscar solo localmente
        matching_genres = self.get_queryset().filter(
            name__icontains=query, is_active=True
        )

        # Convertir entidades a DTOs usando el mapper
        genre_dtos = [
            self.mapper.entity_to_response_dto(genre) for genre in matching_genres
        ]
        serializer = GenreSerializer(genre_dtos, many=True)

        return Response(
            {
                "query": query,
                "results": serializer.data,
                "total": matching_genres.count(),
            },
            status=status.HTTP_200_OK,
        )
