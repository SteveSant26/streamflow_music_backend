from asgiref.sync import async_to_sync
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response

from common.mixins.use_case_api_view_mixin import UseCaseAPIViewMixin

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import GetSongByIdUseCase
from ..mappers import SongMapper
from ..serializers.song_serializers import SongSerializer


@extend_schema_view(
    get=extend_schema(
        tags=["Songs"], description="Get detailed information of a specific song by ID"
    )
)
class SongDetailView(UseCaseAPIViewMixin):
    """Vista para detalles de una canción específica"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.get_song_by_id_use_case = GetSongByIdUseCase(self.repository)
        self.mapper = SongMapper()

    @extend_schema(responses={200: SongSerializer})
    def get(self, request, song_id):
        """Obtiene detalles de una canción"""

        def execute_use_case():
            return async_to_sync(self.get_song_by_id_use_case.execute)(song_id)

        song = self.handle_use_case_execution(execute_use_case)
        song_dto = self.mapper.entity_to_dto(song)
        serializer = SongSerializer(song_dto)

        return Response(serializer.data, status=status.HTTP_200_OK)
