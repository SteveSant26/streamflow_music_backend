from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.mixins.logging_mixin import LoggingMixin

from ...infrastructure.repository.song_repository import SongRepository
from ...use_cases import SaveTrackAsSongUseCase
from ..mappers import SongMapper
from ..serializers.song_serializers import ProcessVideoRequestSerializer, SongSerializer


@extend_schema_view(
    post=extend_schema(
        tags=["Songs"],
        description="Process a YouTube video and save it as a song in the database",
    )
)
class ProcessYouTubeVideoView(APIView, LoggingMixin):
    """Vista para procesar un video específico de YouTube"""

    def __init__(self):
        super().__init__()
        self.repository = SongRepository()
        self.save_track_use_case = SaveTrackAsSongUseCase(self.repository)
        self.mapper = SongMapper()

    @extend_schema(
        request=ProcessVideoRequestSerializer,
        responses={201: SongSerializer, 200: SongSerializer},
    )
    def post(self, request):
        """Procesa un video de YouTube y lo guarda como canción"""
        try:
            serializer = ProcessVideoRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Note: This needs to be adapted to work with the new use case structure
            # The SaveTrackAsSongUseCase expects MusicTrackData, not video_id
            # This view might need to be removed or significantly refactored
            # For now, returning a not implemented response
            return Response(
                {
                    "error": "This endpoint needs to be refactored to work with new architecture"
                },
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        except Exception as e:
            self.logger.error(f"Error processing YouTube video: {str(e)}")
            return Response(
                {"error": "Failed to process video"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
