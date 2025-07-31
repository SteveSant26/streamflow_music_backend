from typing import List

from django.core.paginator import Paginator
from django.db.models import Q

from apps.music_catalog.domain.entities import PaginatedResultEntity, SearchResultEntity
from apps.music_catalog.domain.repository.Imusic_repository import (
    IMusicSearchRepository,
)
from src.common.utils import get_logger

from ..models import AlbumModel, ArtistModel, GenreModel, SongModel

logger = get_logger(__name__)


class MusicSearchRepository(IMusicSearchRepository):
    """Implementación del repositorio de búsqueda musical"""

    def search_all(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> SearchResultEntity:
        """Busca en todas las categorías musicales"""
        songs = self._search_songs(query)[:10]
        artists = self._search_artists(query)[:10]
        albums = self._search_albums(query)[:10]
        genres = self._search_genres(query)[:10]

        return SearchResultEntity(
            query=query,
            songs=songs,
            artists=artists,
            albums=albums,
            genres=genres,
            total_results=len(songs) + len(artists) + len(albums) + len(genres),
        )

    def search_songs_paginated(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> PaginatedResultEntity:
        """Búsqueda paginada de canciones"""
        queryset = (
            SongModel.objects.select_related("artist", "album", "genre")
            .filter(Q(title__icontains=query) | Q(lyrics__icontains=query))
            .filter(is_active=True)
            .order_by("-play_count", "title")
        )

        return self._paginate_queryset(queryset, page, page_size, "songs")

    def search_artists_paginated(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> PaginatedResultEntity:
        """Búsqueda paginada de artistas"""
        queryset = (
            ArtistModel.objects.filter(
                Q(name__icontains=query) | Q(biography__icontains=query)
            )
            .filter(is_active=True)
            .order_by("-followers_count", "name")
        )

        return self._paginate_queryset(queryset, page, page_size, "artists")

    def search_albums_paginated(
        self, query: str, page: int = 1, page_size: int = 20
    ) -> PaginatedResultEntity:
        """Búsqueda paginada de álbumes"""
        queryset = (
            AlbumModel.objects.select_related("artist")
            .filter(Q(title__icontains=query) | Q(description__icontains=query))
            .filter(is_active=True)
            .order_by("-release_date", "title")
        )

        return self._paginate_queryset(queryset, page, page_size, "albums")

    def search_by_filters(
        self, filters: dict, page: int = 1, page_size: int = 20
    ) -> PaginatedResultEntity:
        """Búsqueda con filtros específicos"""
        queryset = SongModel.objects.select_related("artist", "album", "genre").filter(
            is_active=True
        )

        # Aplicar filtros
        if "genre_id" in filters and filters["genre_id"]:
            queryset = queryset.filter(genre_id=filters["genre_id"])

        if "artist_id" in filters and filters["artist_id"]:
            queryset = queryset.filter(artist_id=filters["artist_id"])

        if "album_id" in filters and filters["album_id"]:
            queryset = queryset.filter(album_id=filters["album_id"])

        if "year" in filters and filters["year"]:
            queryset = queryset.filter(album__release_date__year=filters["year"])

        if "duration_min" in filters and filters["duration_min"]:
            queryset = queryset.filter(
                duration_seconds__gte=filters["duration_min"] * 60
            )

        if "duration_max" in filters and filters["duration_max"]:
            queryset = queryset.filter(
                duration_seconds__lte=filters["duration_max"] * 60
            )

        # Ordenar por popularidad
        queryset = queryset.order_by("-play_count", "title")

        return self._paginate_queryset(queryset, page, page_size, "songs")

    # Métodos adicionales requeridos por la interfaz
    def get_paginated_songs(
        self, page: int = 1, page_size: int = 20
    ) -> PaginatedResultEntity:
        """Obtiene canciones paginadas"""
        queryset = (
            SongModel.objects.select_related("artist", "album", "genre")
            .filter(is_active=True)
            .order_by("-play_count", "title")
        )
        return self._paginate_queryset(queryset, page, page_size, "songs")

    def get_paginated_artists(
        self, page: int = 1, page_size: int = 20
    ) -> PaginatedResultEntity:
        """Obtiene artistas paginados"""
        queryset = ArtistModel.objects.filter(is_active=True).order_by(
            "-followers_count", "name"
        )
        return self._paginate_queryset(queryset, page, page_size, "artists")

    def get_paginated_albums(
        self, page: int = 1, page_size: int = 20
    ) -> PaginatedResultEntity:
        """Obtiene álbumes paginados"""
        queryset = (
            AlbumModel.objects.select_related("artist")
            .filter(is_active=True)
            .order_by("-release_date", "title")
        )
        return self._paginate_queryset(queryset, page, page_size, "albums")

    def _search_songs(self, query: str) -> List[dict]:
        """Búsqueda interna de canciones"""
        songs = (
            SongModel.objects.select_related("artist", "album", "genre")
            .filter(Q(title__icontains=query) | Q(lyrics__icontains=query))
            .filter(is_active=True)
            .order_by("-play_count", "title")
        )

        return [self._song_to_dict(song) for song in songs]

    def _search_artists(self, query: str) -> List[dict]:
        """Búsqueda interna de artistas"""
        artists = (
            ArtistModel.objects.filter(
                Q(name__icontains=query) | Q(biography__icontains=query)
            )
            .filter(is_active=True)
            .order_by("-followers_count", "name")
        )

        return [self._artist_to_dict(artist) for artist in artists]

    def _search_albums(self, query: str) -> List[dict]:
        """Búsqueda interna de álbumes"""
        albums = (
            AlbumModel.objects.select_related("artist")
            .filter(Q(title__icontains=query) | Q(description__icontains=query))
            .filter(is_active=True)
            .order_by("-release_date", "title")
        )

        return [self._album_to_dict(album) for album in albums]

    def _search_genres(self, query: str) -> List[dict]:
        """Búsqueda interna de géneros"""
        genres = (
            GenreModel.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
            .filter(is_active=True)
            .order_by("-song_count", "name")
        )

        return [self._genre_to_dict(genre) for genre in genres]

    def _paginate_queryset(
        self, queryset, page: int, page_size: int, result_type: str
    ) -> PaginatedResultEntity:
        """Método helper para paginar querysets"""
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)

        # Convertir resultados según el tipo
        if result_type == "songs":
            results = [self._song_to_dict(item) for item in page_obj]
        elif result_type == "artists":
            results = [self._artist_to_dict(item) for item in page_obj]
        elif result_type == "albums":
            results = [self._album_to_dict(item) for item in page_obj]
        else:
            results = []

        return PaginatedResultEntity(
            results=results,
            page=page,
            page_size=page_size,
            total_pages=paginator.num_pages,
            total_items=paginator.count,
            has_next=page_obj.has_next(),
            has_previous=page_obj.has_previous(),
        )

    def _song_to_dict(self, song) -> dict:
        """Convierte modelo Song a diccionario"""
        return {
            "id": str(song.id),
            "title": song.title,
            "artist_id": str(song.artist.id),
            "artist_name": song.artist.name,
            "album_id": str(song.album.id) if song.album else None,
            "album_title": song.album.title if song.album else None,
            "duration_seconds": song.duration_seconds,
            "file_url": song.file_url,
            "track_number": song.track_number,
            "genre_id": str(song.genre.id) if song.genre else None,
            "genre_name": song.genre.name if song.genre else None,
            "play_count": song.play_count,
            "created_at": song.created_at,
            "updated_at": song.updated_at,
        }

    def _artist_to_dict(self, artist) -> dict:
        """Convierte modelo Artist a diccionario"""
        return {
            "id": str(artist.id),
            "name": artist.name,
            "biography": artist.biography,
            "image_url": artist.image_url,
            "followers_count": artist.followers_count,
            "is_verified": artist.is_verified,
            "created_at": artist.created_at,
            "updated_at": artist.updated_at,
        }

    def _album_to_dict(self, album) -> dict:
        """Convierte modelo Album a diccionario"""
        return {
            "id": str(album.id),
            "title": album.title,
            "artist_id": str(album.artist.id),
            "artist_name": album.artist.name,
            "release_date": album.release_date,
            "description": album.description,
            "cover_image_url": album.cover_image_url,
            "total_tracks": album.total_tracks,
            "play_count": album.play_count,
            "created_at": album.created_at,
            "updated_at": album.updated_at,
        }

    def _genre_to_dict(self, genre) -> dict:
        """Convierte modelo Genre a diccionario"""
        return {
            "id": str(genre.id),
            "name": genre.name,
            "description": genre.description,
            "image_url": genre.image_url,
            "song_count": genre.song_count,
            "created_at": genre.created_at,
            "updated_at": genre.updated_at,
        }
