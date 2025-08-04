from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from common.mixins import UseCaseAPIViewMixin
from common.utils.schema_decorators import paginated_list_endpoint

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import GetMostPlayedSongsUseCase
from ..mappers import SongMapper
from ..serializers.song_serializers import SongListSerializer


class MostPopularSongsView(UseCaseAPIViewMixin):
    """Vista para obtener las canciones más populares/reproducidas"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.get_most_played_songs_use_case = GetMostPlayedSongsUseCase(self.repository)
        self.mapper = SongMapper()

    def get_serializer_class(self) -> type[Serializer]:
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
            self.log_request_info("Get most popular songs")

            # Ejecutar caso de uso usando el método helper
            songs = self.handle_use_case_execution(self.get_most_played_songs_use_case)

            # Convertir a DTOs usando el método helper
            songs_dtos = self.map_entities_to_dtos(songs, self.mapper)

            self.logger.info(f"Retrieved {len(songs_dtos)} most popular songs")
            return self.paginate_and_respond(songs_dtos, request)

        except ValueError:
            self.logger.warning("Invalid limit parameter")
            return Response(
                {"error": "Invalid limit parameter"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            self.logger.error(f"Error getting most popular songs: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
