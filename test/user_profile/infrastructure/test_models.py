"""
Tests para la capa de infraestructura de user_profile
"""
from django.db import IntegrityError
from django.test import TestCase

from apps.user_profile.infrastructure.models.user_profile import UserProfileModel


class TestUserProfileModel(TestCase):
    """Test cases para el modelo UserProfile"""

    def test_create_user_profile(self):
        """Test crear un perfil de usuario"""
        user_profile = UserProfileModel.objects.create(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            profile_picture=None,
        )

        self.assertEqual(user_profile.email, "test@example.com")
        self.assertIsNone(user_profile.profile_picture)
        self.assertTrue(user_profile.is_authenticated)

    def test_user_profile_str_representation(self):
        """Test representación string del modelo"""
        user_profile = UserProfileModel.objects.create(
            id="123e4567-e89b-12d3-a456-426614174000", email="test@example.com"
        )

        self.assertEqual(str(user_profile), "test@example.com")

    def test_user_profile_with_picture(self):
        """Test perfil con foto"""
        picture_url = "https://example.com/picture.jpg"
        user_profile = UserProfileModel.objects.create(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            profile_picture=picture_url,
        )

        self.assertEqual(user_profile.profile_picture, picture_url)

    def test_email_unique_constraint(self):
        """Test que el email debe ser único"""
        # Crear el primer usuario
        UserProfileModel.objects.create(
            id="123e4567-e89b-12d3-a456-426614174000", email="test@example.com"
        )

        # Intentar crear otro con el mismo email debería fallar
        with self.assertRaises(IntegrityError):
            UserProfileModel.objects.create(
                id="123e4567-e89b-12d3-a456-426614174001", email="test@example.com"
            )

    def test_is_authenticated_property(self):
        """Test que is_authenticated siempre retorna True"""
        user_profile = UserProfileModel.objects.create(
            id="123e4567-e89b-12d3-a456-426614174000", email="test@example.com"
        )

        self.assertTrue(user_profile.is_authenticated)


if __name__ == "__main__":
    import django

    django.setup()
    import unittest

    unittest.main()
