from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.albums.api.serializers import AlbumSerializer
from apps.albums.infrastructure.models.album_model import AlbumModel
from common.mixins.logging_mixin import LoggingMixin


@extend_schema_view(
    list=extend_schema(tags=["Albums"]),
    retrieve=extend_schema(tags=["Albums"]),
    search=extend_schema(
        tags=["Albums"],
        description="Search albums (checks YouTube if not found locally)",
    ),
    by_artist=extend_schema(tags=["Albums"], description="Get albums by artist"),
)
class AlbumViewSet(viewsets.ReadOnlyModelViewSet, LoggingMixin):
    """ViewSet para consulta de álbumes (solo lectura, datos de YouTube)"""

    queryset = AlbumModel.objects.all()
    serializer_class = AlbumSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        """Lista todos los álbumes disponibles localmente"""
        self.logger.info("Listing albums from local cache")

        queryset = self.get_queryset().filter(is_active=True)
        serializer = AlbumSerializer(queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """Obtiene un álbum específico, busca en YouTube si no existe localmente"""
        try:
            album = self.get_object()
            self.logger.info(f"Album {album.id} found in local cache")

            serializer = AlbumSerializer(album)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except AlbumModel.DoesNotExist:
            # Si no existe localmente, buscar en YouTube
            album_id = kwargs.get("pk")
            self.logger.info(
                f"Album {album_id} not found locally, searching YouTube..."
            )

            # TODO: Implementar búsqueda en YouTube API
            # youtube_album = fetch_album_from_youtube(album_id)
            # if youtube_album:
            #     album = save_album_to_local_db(youtube_album)
            #     return Response(AlbumSerializer(album).data, status=status.HTTP_200_OK)

            return Response(
                {"detail": "Album not found in local cache or YouTube"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """Busca álbumes por texto, consulta YouTube si no encuentra localmente"""
        query = request.query_params.get("q", "").strip()

        if not query:
            return Response(
                {"error": "Query parameter 'q' is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Searching albums locally for: {query}")

        # Buscar primero en la base de datos local
        local_albums = self.get_queryset().filter(
            title__icontains=query, is_active=True
        )

        if local_albums.exists():
            serializer = AlbumSerializer(local_albums, many=True)
            return Response(
                {"source": "local_cache", "results": serializer.data},
                status=status.HTTP_200_OK,
            )

        # Si no encuentra localmente, buscar en YouTube
        self.logger.info(f"No local results for '{query}', searching YouTube...")

        # TODO: Implementar búsqueda en YouTube API
        # youtube_results = search_albums_on_youtube(query)
        # if youtube_results:
        #     saved_albums = save_albums_to_local_db(youtube_results)
        #     return Response({
        #         "source": "youtube_api",
        #         "results": AlbumSerializer(saved_albums, many=True).data
        #     }, status=status.HTTP_200_OK)

        return Response(
            {
                "source": "not_found",
                "results": [],
                "message": f"No albums found for query: {query}",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], url_path="by-artist")
    def by_artist(self, request):
        """Obtiene álbumes por artista, busca en YouTube si no encuentra localmente"""
        artist_id = request.query_params.get("artist_id")
        artist_name = request.query_params.get("artist_name")

        if not artist_id and not artist_name:
            return Response(
                {"error": "Either 'artist_id' or 'artist_name' parameter is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        self.logger.info(f"Searching albums by artist: {artist_id or artist_name}")

        # Buscar primero localmente
        if artist_id:
            local_albums = self.get_queryset().filter(
                artist_id=artist_id, is_active=True
            )
        else:
            local_albums = self.get_queryset().filter(
                artist_name__icontains=artist_name, is_active=True
            )

        if local_albums.exists():
            serializer = AlbumSerializer(local_albums, many=True)
            return Response(
                {"source": "local_cache", "results": serializer.data},
                status=status.HTTP_200_OK,
            )

        # Si no encuentra localmente, buscar en YouTube
        self.logger.info("No local albums found, searching YouTube...")

        # TODO: Implementar búsqueda por artista en YouTube API
        # youtube_albums = search_albums_by_artist_on_youtube(artist_id or artist_name)
        # if youtube_albums:
        #     saved_albums = save_albums_to_local_db(youtube_albums)
        #     return Response({
        #         "source": "youtube_api",
        #         "results": AlbumSerializer(saved_albums, many=True).data
        #     }, status=status.HTTP_200_OK)

        return Response(
            {
                "source": "not_found",
                "results": [],
                "message": f"No albums found for artist: {artist_id or artist_name}",
            },
            status=status.HTTP_200_OK,
        )
