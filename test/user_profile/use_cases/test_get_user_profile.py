"""
Tests para los casos de uso de user_profile
"""

import unittest
from unittest.mock import Mock

from apps.user_profile.domain.entities import UserEntity
from apps.user_profile.domain.exceptions import UserNotFoundException
from apps.user_profile.use_cases.get_user_profile import GetUserProfile


class TestGetUserProfile(unittest.TestCase):
    """Test cases para GetUserProfile use case"""

    def setUp(self):
        """Setup que se ejecuta antes de cada test"""
        # Mock del repositorio
        self.mock_repository = Mock()
        self.use_case = GetUserProfile(self.mock_repository)

        # Datos de prueba
        self.user_id = "123e4567-e89b-12d3-a456-426614174000"
        self.user_entity = UserEntity(
            id=self.user_id, email="test@example.com", profile_picture=None
        )

    def test_get_user_profile_success(self):
        """Test obtener perfil de usuario exitosamente"""
        # Arrange
        self.mock_repository.get_by_id.return_value = self.user_entity

        # Act
        result = self.use_case.execute(self.user_id)

        # Assert
        self.assertEqual(result, self.user_entity)
        self.mock_repository.get_by_id.assert_called_once_with(self.user_id)

    def test_get_user_profile_not_found(self):
        """Test cuando el usuario no existe"""
        # Arrange
        self.mock_repository.get_by_id.return_value = None

        # Act & Assert
        with self.assertRaises(UserNotFoundException):
            self.use_case.execute(self.user_id)

        self.mock_repository.get_by_id.assert_called_once_with(self.user_id)

    def test_get_user_profile_repository_called_correctly(self):
        """Test que el repositorio se llama con los parámetros correctos"""
        # Arrange
        self.mock_repository.get_by_id.return_value = self.user_entity

        # Act
        self.use_case.execute(self.user_id)

        # Assert
        self.mock_repository.get_by_id.assert_called_once_with(self.user_id)


if __name__ == "__main__":
    unittest.main()
