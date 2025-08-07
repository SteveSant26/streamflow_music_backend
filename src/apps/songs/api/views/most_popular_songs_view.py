<<<<<<< HEAD
from asgiref.sync import async_to_sync
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from common.mixins.paginated_api_view import PaginatedAPIView
=======
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from common.mixins import UseCaseAPIViewMixin
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
from common.utils.schema_decorators import paginated_list_endpoint

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import GetMostPlayedSongsUseCase
from ..mappers import SongMapper
from ..serializers.song_serializers import SongListSerializer


<<<<<<< HEAD
class MostPopularSongsView(PaginatedAPIView):
    """Vista para obtener las canciones más populares/reproducidas"""

    permission_classes = [AllowAny]

=======
class MostPopularSongsView(UseCaseAPIViewMixin):
    """Vista para obtener las canciones más populares/reproducidas"""

>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
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
<<<<<<< HEAD
            # Ejecutar caso de uso
            songs = async_to_sync(self.get_most_played_songs_use_case.execute)()

            # Convertir a DTOs
            songs_dtos = [self.mapper.entity_to_dto(song) for song in songs]

            # Usar el método heredado del PaginationMixin para paginar y responder
=======
            self.log_request_info("Get most popular songs")

            # Ejecutar caso de uso usando el método helper
            songs = self.handle_use_case_execution(self.get_most_played_songs_use_case)

            # Convertir a DTOs usando el método helper
            songs_dtos = self.map_entities_to_dtos(songs, self.mapper)

>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            self.logger.info(f"Retrieved {len(songs_dtos)} most popular songs")
            return self.paginate_and_respond(songs_dtos, request)

        except ValueError:
            self.logger.warning("Invalid limit parameter")
            return Response(
<<<<<<< HEAD
                {"error": "Invalid limit parameter. Must be an integer."},
                status=status.HTTP_400_BAD_REQUEST,
=======
                {"error": "Invalid limit parameter"}, status=status.HTTP_400_BAD_REQUEST
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
            )
        except Exception as e:
            self.logger.error(f"Error getting most popular songs: {str(e)}")
            return Response(
<<<<<<< HEAD
                {"error": "Failed to retrieve most popular songs"},
=======
                {"error": "Internal server error"},
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
