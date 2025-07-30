"""
Excepciones específicas del dominio de catálogo musical
"""


class MusicCatalogException(Exception):
    """Excepción base para errores del catálogo musical"""
    def __init__(self, message: str = "Error en el catálogo musical"):
        self.message = message
        super().__init__(self.message)


class SongNotFoundException(MusicCatalogException):
    """Excepción cuando no se encuentra una canción"""
    def __init__(self, song_id: str):
        message = f"Canción no encontrada: {song_id}"
        super().__init__(message)


class ArtistNotFoundException(MusicCatalogException):
    """Excepción cuando no se encuentra un artista"""
    def __init__(self, artist_id: str):
        message = f"Artista no encontrado: {artist_id}"
        super().__init__(message)


class AlbumNotFoundException(MusicCatalogException):
    """Excepción cuando no se encuentra un álbum"""
    def __init__(self, album_id: str):
        message = f"Álbum no encontrado: {album_id}"
        super().__init__(message)


class GenreNotFoundException(MusicCatalogException):
    """Excepción cuando no se encuentra un género"""
    def __init__(self, genre_id: str):
        message = f"Género no encontrado: {genre_id}"
        super().__init__(message)


class InvalidSearchQueryException(MusicCatalogException):
    """Excepción para consultas de búsqueda inválidas"""
    def __init__(self, query: str):
        message = f"Consulta de búsqueda inválida: {query}"
        super().__init__(message)


class DuplicateResourceException(MusicCatalogException):
    """Excepción cuando se intenta crear un recurso duplicado"""
    def __init__(self, resource_type: str, identifier: str):
        message = f"{resource_type} ya existe: {identifier}"
        super().__init__(message)


class InvalidAudioFileException(MusicCatalogException):
    """Excepción para archivos de audio inválidos"""
    def __init__(self, file_path: str):
        message = f"Archivo de audio inválido: {file_path}"
        super().__init__(message)
