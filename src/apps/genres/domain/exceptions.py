from typing import Optional

from src.common.exceptions import DomainException, NotFoundException


class GenreNotFoundException(NotFoundException):
    def __init__(self, genre_id: str):
        super().__init__(f"Género con ID {genre_id} no encontrado.")


class GenreCreationException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)


class GenreUpdateException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)


class GenreSearchException(DomainException):
    def __init__(self, search_term: str, message: Optional[str] = None):
        if message is None:
            message = f"Error en la búsqueda de géneros con término: {search_term}"
        super().__init__(message)
