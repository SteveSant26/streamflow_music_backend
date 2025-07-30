from src.common.exceptions import NotFoundException


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: str):
        super().__init__(f"User con ID {user_id} no encontrado.")


class UserProfilePictureUploadException(Exception):
    def __init__(self, message: str):
        super().__init__(message)
