from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from common.mixins.paginated_api_view import PaginatedAPIView
from common.utils.schema_decorators import paginated_list_endpoint

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import GetMostPlayedSongsUseCase
from ..mappers import SongMapper
from ..serializers.song_serializers import SongListSerializer


class MostPopularSongsView(PaginatedAPIView):
    """Vista para obtener las canciones más populares/reproducidas"""

    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.get_most_played_songs_use_case = GetMostPlayedSongsUseCase(self.repository)
        self.mapper = SongMapper()

    def get_serializer_class(self):
        """Return the serializer class for this view"""
        return SongListSerializer

    @paginated_list_endpoint(
        serializer_class=SongListSerializer,
        tags=["Songs"],
        description="Get the most popular/played songs from the database",
    )
    def get(self, request):
        """Obtiene las canciones más populares/reproducidas"""
        try:
            limit = int(request.GET.get("limit", 100))

            # Validar límite
            if limit <= 0:
                return Response(
                    {"error": "Limit must be greater than 0"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if limit > 100:
                return Response(
                    {"error": "Limit cannot exceed 100"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Ejecutar caso de uso
            songs = async_to_sync(self.get_most_played_songs_use_case.execute)(limit)

            # Convertir a DTOs
            songs_dtos = [self.mapper.entity_to_dto(song) for song in songs]

            # Usar el método heredado del PaginationMixin para paginar y responder
            self.logger.info(f"Retrieved {len(songs_dtos)} most popular songs")
            return self.paginate_and_respond(songs_dtos, request)

        except ValueError:
            self.logger.warning("Invalid limit parameter")
            return Response(
                {"error": "Invalid limit parameter. Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            self.logger.error(f"Error getting most popular songs: {str(e)}")
            return Response(
                {"error": "Failed to retrieve most popular songs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
