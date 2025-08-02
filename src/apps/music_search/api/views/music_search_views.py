"""
ViewSet principal para búsquedas musicales integradas.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from apps.music_search.api.serializers import (
    QuickSearchSerializer,
    SearchHistorySerializer,
    SearchRequestSerializer,
)
from common.mixins.logging_mixin import LoggingMixin


@extend_schema_view(
    search=extend_schema(
        tags=["Music Search"], description="Buscar contenido musical (local + YouTube)"
    ),
    quick_search=extend_schema(
        tags=["Music Search"], description="Búsqueda rápida para autocompletado"
    ),
    history=extend_schema(
        tags=["Music Search"], description="Historial de búsquedas del usuario"
    ),
    youtube_import=extend_schema(
        tags=["Music Search"], description="Importar contenido específico desde YouTube"
    ),
)
class MusicSearchViewSet(ViewSet, LoggingMixin):
    """ViewSet para búsquedas musicales integradas con YouTube"""

    def get_permissions(self):
        """Permisos por acción"""
        action_permissions = {
            "search": AllowAny,
            "quick_search": AllowAny,
            "history": IsAuthenticated,
            "youtube_import": IsAuthenticated,
        }
        permission_class = action_permissions.get(self.action, AllowAny)
        return [permission_class()]

    def get_serializer_class(self):
        """Selecciona el serializer según la acción"""
        action_to_serializer = {
            "search": SearchRequestSerializer,
            "quick_search": QuickSearchSerializer,
            "history": SearchHistorySerializer,
        }
        return action_to_serializer.get(self.action, SearchRequestSerializer)

    @action(detail=False, methods=["post"], url_path="search")
    def search(self, request):
        """Búsqueda unificada: primero local, luego YouTube si es necesario"""
        self.logger.info("Performing unified music search")

        serializer = SearchRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Usar request.data directamente ya que ya está validado
        query = request.data.get("query", "")
        search_types = request.data.get(
            "types", ["artists", "albums", "songs", "genres"]
        )

        self.logger.info(f"Searching for: '{query}' in types: {search_types}")

        # Estructura de respuesta
        response_data = {
            "query": query,
            "artists": [],
            "albums": [],
            "songs": [],
            "genres": [],
            "total_results": 0,
            "search_time_ms": 0.0,
            "sources": {"local_cache": True, "youtube_api": False},
        }

        local_results_found = False

        # 1. Buscar en caché local primero
        if "songs" in search_types:
            # TODO: Buscar en modelo Song local
            pass

        if "artists" in search_types:
            # TODO: Buscar en modelo Artist local
            pass

        if "albums" in search_types:
            # TODO: Buscar en modelo Album local
            pass

        if "genres" in search_types:
            # TODO: Buscar en modelo Genre local
            pass

        # 2. Si no encuentra suficientes resultados localmente, buscar en YouTube
        if not local_results_found:
            self.logger.info(
                f"No sufficient local results for '{query}', searching YouTube..."
            )
            response_data["sources"]["youtube_api"] = True

            # Simulación de resultados de YouTube
            if query.strip():
                response_data["songs"] = [
                    {
                        "id": "yt-song-123",
                        "title": f"YouTube Song: {query}",
                        "artist_name": "YouTube Artist",
                        "youtube_video_id": "abc123def456",
                        "audio_downloaded": False,
                        "source": "youtube_api",
                    }
                ]

        # Calcular total de resultados
        response_data["total_results"] = sum(
            [
                len(response_data["artists"]),
                len(response_data["albums"]),
                len(response_data["songs"]),
                len(response_data["genres"]),
            ]
        )

        return Response(response_data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="quick")
    def quick_search(self, request):
        """Búsqueda rápida para autocompletado (solo caché local)"""
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Quick search for: '{query}'")

        # Búsqueda rápida solo en caché local para rendimiento
        suggestions = []

        if len(query) >= 2:  # Mínimo 2 caracteres
            # Simulación
            suggestions = [
                {"title": f"{query} - Song", "type": "song", "id": "song-123"},
                {"title": f"{query} Artist", "type": "artist", "id": "artist-123"},
                {"title": f"{query} Album", "type": "album", "id": "album-123"},
            ]

        return Response(
            {"query": query, "suggestions": suggestions[:6]},  # Máximo 6 sugerencias
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="history")
    def history(self, request):
        """Obtiene el historial de búsquedas del usuario"""
        self.logger.info(f"Getting search history for user {request.user.id}")

        # Simulación
        history_data = [
            {
                "id": "search-1",
                "query_text": "rock music",
                "user_id": str(request.user.id),
                "results_count": 15,
                "created_at": "2025-01-31T10:00:00Z",
            },
            {
                "id": "search-2",
                "query_text": "pop songs",
                "user_id": str(request.user.id),
                "results_count": 8,
                "created_at": "2025-01-31T09:30:00Z",
            },
        ]

        return Response({"history": history_data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="youtube-import")
    def youtube_import(self, request):
        """Importa contenido específico desde YouTube y lo guarda localmente"""
        self.logger.info(f"User {request.user.id} is requesting YouTube import")

        youtube_url = request.data.get("youtube_url")
        content_type = request.data.get(
            "content_type", "song"
        )  # song, playlist, channel

        if not youtube_url:
            return Response(
                {"error": "youtube_url is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        self.logger.info(
            f"Importing from YouTube: {youtube_url} (type: {content_type})"
        )

        return Response(
            {
                "message": "YouTube import started",
                "url": youtube_url,
                "content_type": content_type,
                "status": "processing",
                "note": "Content will be processed in background",
            },
            status=status.HTTP_202_ACCEPTED,
        )
