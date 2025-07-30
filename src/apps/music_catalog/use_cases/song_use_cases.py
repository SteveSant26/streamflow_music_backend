from typing import List, Optional
from ..domain.repository.Imusic_repository import ISongRepository
from ..domain.entities import SongEntity
from ..domain.exceptions import SongNotFoundException
from src.common.utils import get_logger

logger = get_logger(__name__)


class SongUseCases:
    """Casos de uso para canciones"""
    
    def __init__(self, song_repository: ISongRepository):
        self.song_repository = song_repository
    
    def get_song_by_id(self, song_id: str) -> Optional[SongEntity]:
        """Obtiene una canción por ID"""
        logger.info(f"Getting song with ID: {song_id}")
        return self.song_repository.get_by_id(song_id)
    
    def get_all_songs(self) -> List[SongEntity]:
        """Obtiene todas las canciones"""
        logger.info("Getting all songs")
        return self.song_repository.get_all()
    
    def get_songs_by_artist(self, artist_id: str) -> List[SongEntity]:
        """Obtiene canciones de un artista"""
        logger.info(f"Getting songs by artist: {artist_id}")
        return self.song_repository.get_by_artist(artist_id)
    
    def get_songs_by_album(self, album_id: str) -> List[SongEntity]:
        """Obtiene canciones de un álbum"""
        logger.info(f"Getting songs by album: {album_id}")
        return self.song_repository.get_by_album(album_id)
    
    def get_songs_by_genre(self, genre_id: str) -> List[SongEntity]:
        """Obtiene canciones de un género"""
        logger.info(f"Getting songs by genre: {genre_id}")
        return self.song_repository.get_by_genre(genre_id)
    
    def get_popular_songs(self, limit: int = 50) -> List[SongEntity]:
        """Obtiene canciones populares"""
        logger.info(f"Getting popular songs with limit: {limit}")
        return self.song_repository.get_popular_songs(limit)
    
    def search_songs_by_title(self, title: str) -> List[SongEntity]:
        """Busca canciones por título"""
        logger.info(f"Searching songs by title: {title}")
        return self.song_repository.search_by_title(title)
    
    def play_song(self, song_id: str) -> Optional[SongEntity]:
        """Reproduce una canción (incrementa contador)"""
        logger.info(f"Playing song: {song_id}")
        if self.song_repository.increment_play_count(song_id):
            return self.song_repository.get_by_id(song_id)
        return None


class GetSong:
    """Caso de uso para obtener una canción específica"""
    
    def __init__(self, song_repository: ISongRepository):
        self.song_repository = song_repository
    
    def execute(self, song_id: str) -> SongEntity:
        """
        Obtiene una canción por ID
        
        Args:
            song_id: ID de la canción
            
        Returns:
            SongEntity: Canción encontrada
            
        Raises:
            SongNotFoundException: Si la canción no existe
        """
        logger.info(f"Getting song with ID: {song_id}")
        
        song = self.song_repository.get_by_id(song_id)
        if not song:
            raise SongNotFoundException(song_id)
        
        logger.info(f"Song retrieved: {song.title} by {song.artist_name}")
        return song


class GetSongsByArtist:
    """Caso de uso para obtener canciones de un artista"""
    
    def __init__(self, song_repository: ISongRepository):
        self.song_repository = song_repository
    
    def execute(self, artist_id: str) -> List[SongEntity]:
        """
        Obtiene todas las canciones de un artista
        
        Args:
            artist_id: ID del artista
            
        Returns:
            List[SongEntity]: Lista de canciones del artista
        """
        logger.info(f"Getting songs for artist: {artist_id}")
        
        songs = self.song_repository.get_by_artist(artist_id)
        
        logger.info(f"Found {len(songs)} songs for artist {artist_id}")
        return songs


class GetSongsByAlbum:
    """Caso de uso para obtener canciones de un álbum"""
    
    def __init__(self, song_repository: ISongRepository):
        self.song_repository = song_repository
    
    def execute(self, album_id: str) -> List[SongEntity]:
        """
        Obtiene todas las canciones de un álbum
        
        Args:
            album_id: ID del álbum
            
        Returns:
            List[SongEntity]: Lista de canciones del álbum ordenadas por track_number
        """
        logger.info(f"Getting songs for album: {album_id}")
        
        songs = self.song_repository.get_by_album(album_id)
        
        # Ordenar por número de pista
        songs.sort(key=lambda x: x.track_number or 0)
        
        logger.info(f"Found {len(songs)} songs for album {album_id}")
        return songs


class GetPopularSongs:
    """Caso de uso para obtener canciones populares"""
    
    def __init__(self, song_repository: ISongRepository):
        self.song_repository = song_repository
    
    def execute(self, limit: int = 50) -> List[SongEntity]:
        """
        Obtiene las canciones más populares
        
        Args:
            limit: Número máximo de canciones a retornar
            
        Returns:
            List[SongEntity]: Lista de canciones populares ordenadas por play_count
        """
        logger.info(f"Getting top {limit} popular songs")
        
        songs = self.song_repository.get_popular_songs(limit)
        
        logger.info(f"Retrieved {len(songs)} popular songs")
        return songs


class PlaySong:
    """Caso de uso para reproducir una canción (incrementa el contador)"""
    
    def __init__(self, song_repository: ISongRepository):
        self.song_repository = song_repository
    
    def execute(self, song_id: str) -> SongEntity:
        """
        Reproduce una canción incrementando su contador de reproducciones
        
        Args:
            song_id: ID de la canción
            
        Returns:
            SongEntity: Canción con el contador actualizado
            
        Raises:
            SongNotFoundException: Si la canción no existe
        """
        logger.info(f"Playing song: {song_id}")
        
        # Obtener la canción
        song = self.song_repository.get_by_id(song_id)
        if not song:
            raise SongNotFoundException(song_id)
        
        # Incrementar contador de reproducciones
        success = self.song_repository.increment_play_count(song_id)
        
        if success:
            song.play_count += 1
            logger.info(f"Play count incremented for song {song_id}. New count: {song.play_count}")
        else:
            logger.warning(f"Failed to increment play count for song {song_id}")
        
        return song


class SearchSongs:
    """Caso de uso para buscar canciones por título"""
    
    def __init__(self, song_repository: ISongRepository):
        self.song_repository = song_repository
    
    def execute(self, query: str) -> List[SongEntity]:
        """
        Busca canciones por título
        
        Args:
            query: Término de búsqueda
            
        Returns:
            List[SongEntity]: Lista de canciones que coinciden con la búsqueda
        """
        logger.info(f"Searching songs with query: {query}")
        
        if not query or len(query.strip()) < 2:
            logger.warning("Search query too short")
            return []
        
        songs = self.song_repository.search_by_title(query.strip())
        
        logger.info(f"Found {len(songs)} songs matching '{query}'")
        return songs
