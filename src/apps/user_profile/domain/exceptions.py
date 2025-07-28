from src.common.exceptions import NotFoundException


class UserNotFoundException(NotFoundException):
    def __init__(self, user_id: str):
        super().__init__(f"User con ID {user_id} no encontrado.")
