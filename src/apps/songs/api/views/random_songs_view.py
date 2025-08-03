from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from common.factories import MediaServiceFactory
from common.mixins.paginated_api_view import PaginatedAPIView
from common.utils.schema_decorators import paginated_list_endpoint

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import GetRandomSongsUseCase
from ..dtos import RandomSongsRequestDTO
from ..mappers import SongMapper
from ..serializers.song_serializers import SongListSerializer


@extend_schema_view(
    get=extend_schema(
        tags=["Songs"],
        description="Get random songs from the database with optional refresh from YouTube",
    )
)
class RandomSongsView(PaginatedAPIView):
    """Vista para obtener canciones aleatorias"""

    permission_classes = [AllowAny]

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.music_service = MediaServiceFactory.create_music_service()
        self.get_random_songs_use_case = GetRandomSongsUseCase(
            self.repository, self.music_service
        )
        self.mapper = SongMapper()

    def get_serializer_class(self) -> type[Serializer]:
        """Override this method to specify the serializer"""
        return SongListSerializer

    @paginated_list_endpoint(
        serializer_class=SongListSerializer,
        tags=["Songs"],
        description="Get random songs from the database",
    )
    def get(self, request):
        """Obtiene canciones aleatorias"""
        try:
            count = int(request.GET.get("count", 6))
            force_refresh = request.GET.get("force_refresh", "false").lower() == "true"

            request_dto = RandomSongsRequestDTO(
                count=count, force_refresh=force_refresh
            )

            # Ejecutar función async directamente sin asyncio.run()
            songs = async_to_sync(self.get_random_songs_use_case.execute)(request_dto)

            songs_dtos = [self.mapper.entity_to_dto(song) for song in songs]

            # Usar el método heredado del PaginationMixin
            return self.paginate_and_respond(songs_dtos, request)

        except Exception as e:
            self.logger.error(f"Error getting random songs: {str(e)}")
            return Response(
                {"error": "Failed to retrieve random songs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
