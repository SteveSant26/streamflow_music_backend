from common.exceptions import DomainException, NotFoundException


class SongNotFoundException(NotFoundException):
    def __init__(self, song_id: str):
        super().__init__(f"Song con ID {song_id} no encontrado.")


class SongCreationException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)


class SongUpdateException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)


class SongPlayCountException(DomainException):
    def __init__(self, message: str):
        super().__init__(message)
