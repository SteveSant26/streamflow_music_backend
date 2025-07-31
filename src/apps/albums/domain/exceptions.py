from common.exceptions.base import DomainException
from src.common.exceptions import NotFoundException


class AlbumNotFoundException(NotFoundException):
    def __init__(self, album_id: str):
        super().__init__(f"Album con ID {album_id} no encontrado.")


class AlbumCreationException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)


class AlbumUpdateException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)
