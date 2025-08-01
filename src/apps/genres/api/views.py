from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.genres.api.serializers import GenreSerializer
from apps.genres.infrastructure.models.genre_model import GenreModel
from common.mixins.logging_mixin import LoggingMixin


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

    def list(self, request, *args, **kwargs):
        """Lista todos los géneros disponibles localmente"""
        self.logger.info("Listing genres from local cache")

        queryset = self.get_queryset().filter(is_active=True)
        serializer = GenreSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Obtiene un género específico"""
        genre = self.get_object()
        self.logger.info(f"Retrieving genre {genre.id}")

        serializer = GenreSerializer(genre)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="popular")
    def popular(self, request):
        """Obtiene los géneros más populares de la caché local"""
        self.logger.info("Getting popular genres")

        popular_genres = (
            self.get_queryset()
            .filter(is_active=True)
            .order_by("-popularity_score")[:10]
        )

        serializer = GenreSerializer(popular_genres, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

        serializer = GenreSerializer(matching_genres, many=True)
        return Response(
            {
                "query": query,
                "results": serializer.data,
                "total": matching_genres.count(),
            },
            status=status.HTTP_200_OK,
        )
