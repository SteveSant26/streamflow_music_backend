from common.exceptions.base import DomainException
from src.common.exceptions import NotFoundException


class ArtistNotFoundException(NotFoundException):
    def __init__(self, artist_id: str):
        super().__init__(f"Artist con ID {artist_id} no encontrado.")


class ArtistCreationException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)


class ArtistUpdateException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)
