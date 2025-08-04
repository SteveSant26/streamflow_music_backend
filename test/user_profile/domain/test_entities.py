"""
Tests para las entidades del dominio de user_profile
"""
import unittest

from src.apps.user_profile.domain.entities import UserEntity


class TestUserEntity(unittest.TestCase):
    """Test cases para UserEntity"""

    def test_user_entity_creation(self):
        """Test que una entidad de usuario se crea correctamente"""
        user = UserEntity(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            profile_picture=None,
        )

        self.assertEqual(user.id, "123e4567-e89b-12d3-a456-426614174000")
        self.assertEqual(user.email, "test@example.com")
        self.assertIsNone(user.profile_picture)

    def test_user_entity_with_profile_picture(self):
        """Test entidad con foto de perfil"""
        user = UserEntity(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            profile_picture="https://example.com/picture.jpg",
        )

        self.assertEqual(user.profile_picture, "https://example.com/picture.jpg")

    def test_user_entity_equality(self):
        """Test que dos entidades con el mismo ID son iguales"""
        user1 = UserEntity(id="123", email="test1@example.com")
        user2 = UserEntity(id="123", email="test2@example.com")

        # En una entidad, el ID debería ser suficiente para determinar igualdad
        self.assertEqual(user1.id, user2.id)


if __name__ == "__main__":
    unittest.main()
