"""
Excepciones específicas del dominio de playlists
"""

from common.exceptions import DomainException, NotFoundException


class PlaylistNotFoundException(NotFoundException):
    """Excepción lanzada cuando no se encuentra una playlist"""


class PlaylistValidationException(DomainException):
    """Excepción lanzada cuando hay un error de validación en playlist"""


class PlaylistPermissionException(DomainException):
    """Excepción lanzada cuando no se tienen permisos para la playlist"""


class PlaylistSongNotFoundException(NotFoundException):
    """Excepción lanzada cuando no se encuentra una canción en la playlist"""


class PlaylistSongAlreadyExistsException(DomainException):
    """Excepción lanzada cuando la canción ya existe en la playlist"""


class PlaylistImageUploadException(DomainException):
    """Excepción lanzada cuando hay un error al subir la imagen de la playlist"""
