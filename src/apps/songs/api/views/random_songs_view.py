from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from apps.songs.infrastructure.filters import SongModelFilter
from common.factories.unified_music_service_factory import get_music_service
from common.mixins import UseCaseAPIViewMixin
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
class RandomSongsView(UseCaseAPIViewMixin):
    """Vista para obtener canciones aleatorias"""

    filterset_class = SongModelFilter

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.music_service = get_music_service()
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
        parameters=[
            OpenApiParameter(
                name="force_refresh",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Whether to include YouTube results",
            ),
        ],
    )
    def get(self, request):
        """Obtiene canciones aleatorias"""
        try:
            self.log_request_info("Get random songs")

            page_size = self.paginator.page_size
            force_refresh = request.GET.get("force_refresh", "false").lower() == "true"

            request_dto = RandomSongsRequestDTO(
                count=page_size, force_refresh=force_refresh
            )

            # Ejecutar caso de uso usando el método helper
            songs = self.handle_use_case_execution(
                self.get_random_songs_use_case, request_dto
            )

            # Convertir a DTOs usando el método helper
            songs_dtos = self.map_entities_to_dtos(songs, self.mapper)

            # Usar el método heredado del PaginationMixin
            return self.paginate_and_respond(songs_dtos, request)

        except Exception as e:
            self.logger.error(f"Error getting random songs: {str(e)}")
            return Response(
                {"error": "Failed to retrieve random songs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
