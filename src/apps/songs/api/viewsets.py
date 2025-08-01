from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.songs.api.serializers import (
    ProcessVideoRequestSerializer,
    SongListSerializer,
    SongSerializer,
)
from apps.songs.infrastructure.models.song_model import SongModel
from common.mixins.logging_mixin import LoggingMixin


@extend_schema_view(
    list=extend_schema(tags=["Songs"]),
    retrieve=extend_schema(tags=["Songs"]),
    search=extend_schema(
        tags=["Songs"], description="Search songs (checks YouTube if not found locally)"
    ),
    random=extend_schema(
        tags=["Songs"], description="Get random songs from local cache"
    ),
    download_from_youtube=extend_schema(
        tags=["Songs"],
        description="Download song from YouTube and save to local storage",
    ),
)
class SongViewSet(viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para gestión de canciones (integración con YouTube)"""

    queryset = SongModel.objects.all()
    serializer_class = SongSerializer

    def get_permissions(self):
        """Permisos por acción"""
        action_permissions = {
            "list": AllowAny,
            "retrieve": AllowAny,
            "search": AllowAny,
            "random": AllowAny,
            "download_from_youtube": IsAuthenticated,
        }
        permission_class = action_permissions.get(self.action, AllowAny)
        return [permission_class()]

    def get_serializer_class(self):
        """Selecciona el serializer según la acción"""
        action_to_serializer = {
            "list": SongListSerializer,
            "retrieve": SongSerializer,
            "download_from_youtube": ProcessVideoRequestSerializer,
        }
        return action_to_serializer.get(self.action, SongSerializer)

    def list(self, request, *args, **kwargs):
        """Lista todas las canciones disponibles localmente"""
        self.logger.info("Listing songs from local cache")

        queryset = self.get_queryset().filter(is_active=True)
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = SongListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = SongListSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Obtiene una canción específica y actualiza contador de reproducciones"""
        song = self.get_object()
        self.logger.info(f"Retrieving song {song.id}")

        # Incrementar contador de reproducciones
        song.play_count += 1
        song.save()

        serializer = SongSerializer(song)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Busca canciones por texto, consulta YouTube si no encuentra localmente"""
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Searching songs locally for: {query}")

        # Buscar primero en la base de datos local
        local_songs = self.get_queryset().filter(
            title__icontains=query, is_active=True
        ) | self.get_queryset().filter(artist_name__icontains=query, is_active=True)

        if local_songs.exists():
            serializer = SongListSerializer(local_songs, many=True)
            return Response(
                {
                    "source": "local_cache",
                    "query": query,
                    "results": serializer.data,
                    "total": local_songs.count(),
                },
                status=status.HTTP_200_OK,
            )

        # Si no encuentra localmente, buscar en YouTube
        self.logger.info(f"No local results for '{query}', searching YouTube...")

        # TODO: Implementar búsqueda en YouTube API
        # youtube_results = search_songs_on_youtube(query)
        # if youtube_results:
        #     # Guardar metadatos en base de datos (sin descargar audio aún)
        #     saved_songs = save_song_metadata_to_local_db(youtube_results)
        #     return Response({
        #         "source": "youtube_api",
        #         "query": query,
        #         "results": SongListSerializer(saved_songs, many=True).data,
        #         "total": len(saved_songs),
        #         "note": "Audio not downloaded yet. Use download_from_youtube to cache audio files."
        #     }, status=status.HTTP_200_OK)

        return Response(
            {
                "source": "not_found",
                "query": query,
                "results": [],
                "total": 0,
                "message": f"No songs found for query: {query}",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="random")
    def random(self, request):
        """Obtiene canciones aleatorias de la caché local"""
        count = min(int(request.query_params.get("count", 10)), 50)  # Máximo 50

        self.logger.info(f"Getting {count} random songs from local cache")

        random_songs = self.get_queryset().filter(is_active=True).order_by("?")[:count]

        serializer = SongListSerializer(random_songs, many=True)
        return Response(
            {
                "source": "local_cache",
                "results": serializer.data,
                "total": random_songs.count(),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="download-from-youtube")
    def download_from_youtube(self, request):
        """Descarga una canción de YouTube y la guarda en el storage local"""
        self.logger.info(f"User {request.user.id} is requesting YouTube download")

        serializer = ProcessVideoRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        youtube_url = serializer.validated_data.get("youtube_url")
        youtube_video_id = serializer.validated_data.get("youtube_video_id")

        if not youtube_url and not youtube_video_id:
            return Response(
                {"error": "Either youtube_url or youtube_video_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(
            f"Processing YouTube content: {youtube_url or youtube_video_id}"
        )

        # TODO: Implementar descarga desde YouTube
        # 1. Extraer metadatos del video
        # 2. Descargar audio
        # 3. Subir a storage (Supabase)
        # 4. Guardar información en base de datos
        # 5. Retornar información de la canción guardada

        # video_info = extract_youtube_video_info(youtube_url or youtube_video_id)
        # audio_file = download_audio_from_youtube(video_info)
        # storage_url = upload_audio_to_storage(audio_file)
        # song = save_complete_song_to_db(video_info, storage_url)

        self.logger.info("YouTube download processing started (background task)")

        return Response(
            {
                "message": "YouTube download started",
                "status": "processing",
                "url": youtube_url,
                "video_id": youtube_video_id,
                "note": "Audio file will be processed in background. Check status later.",
            },
            status=status.HTTP_202_ACCEPTED,
        )
