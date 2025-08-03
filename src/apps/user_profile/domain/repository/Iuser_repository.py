from abc import ABC, abstractmethod
from typing import Optional

from apps.user_profile.domain.entities import UserProfileEntity


class IUserRepository(ABC):
    """
    Interface for user repository.

    Esta interfaz no debe depender de implementaciones concretas de infraestructura.
    El tipo UserProfileModelType será especificado por la implementación concreta.
    """

    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserProfileEntity]:
        """Obtiene un usuario por email"""
