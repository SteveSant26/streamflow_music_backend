from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from common.factories.unified_music_service_factory import get_music_service
from common.mixins import UseCaseAPIViewMixin
from common.utils.schema_decorators import paginated_list_endpoint

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import SearchSongsUseCase
from ..dtos import SongSearchRequestDTO
from ..mappers import SongMapper
from ..serializers.song_serializers import SongListSerializer


@extend_schema_view(
    get=extend_schema(
        tags=["Songs"],
        description="Search for songs in the database and optionally from YouTube",
    )
)
class SearchSongsView(UseCaseAPIViewMixin):
    """Vista para buscar canciones"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()

        self.music_service = get_music_service()
        self.search_songs_use_case = SearchSongsUseCase(
            self.repository, self.music_service
        )
        self.mapper = SongMapper()

    def get_serializer_class(self) -> type[Serializer]:
        """Override this method to specify the serializer"""
        return SongListSerializer

    @paginated_list_endpoint(
        serializer_class=SongListSerializer,
        tags=["Songs"],
        description="Search for songs in the database and optionally from YouTube",
        parameters=[
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search query for song names",
            ),
            OpenApiParameter(
                name="include_youtube",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Whether to include YouTube results",
            ),
        ],
    )
    def get(self, request):
        """Busca canciones"""
        try:
            query = request.GET.get("q")
            if not query:
                return Response(
                    {"error": "Query parameter 'q' is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            self.log_request_info("Search songs", f"query: {query}")

            page_size = self.paginator.page_size

            include_youtube = (
                request.GET.get("include_youtube", "true").lower() == "true"
            )

            request_dto = SongSearchRequestDTO(
                query=query, limit=page_size, include_youtube=include_youtube
            )

            # Ejecutar caso de uso usando el método helper
            songs = self.handle_use_case_execution(
                self.search_songs_use_case, request_dto
            )

            # Convertir a DTOs usando el método helper
            songs_dtos = self.map_entities_to_dtos(songs, self.mapper)

            # Usar el método heredado del PaginationMixin
            return self.paginate_and_respond(songs_dtos, request)

        except Exception as e:
            self.logger.error(f"Error searching songs: {str(e)}")
            return Response(
                {"error": "Failed to search songs"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
