"""
Tests para el repositorio de user_profile
"""
import unittest
from uuid import uuid4

from django.test import TestCase

from apps.user_profile.domain.entities import UserEntity
from apps.user_profile.infrastructure.models.user_profile import UserProfile
from apps.user_profile.infrastructure.repository import UserRepository


class TestUserRepository(TestCase):
    """Test cases para UserRepository"""

    def setUp(self):
        """Setup que se ejecuta antes de cada test"""
        self.repository = UserRepository()
        self.user_id = str(uuid4())
        self.user_email = "test@example.com"

        # Crear un usuario de prueba en la BD
        self.user_model = UserProfile.objects.create(
            id=self.user_id, email=self.user_email, profile_picture=None
        )

    def test_get_by_id_existing_user(self):
        """Test obtener usuario existente por ID"""
        result = self.repository.get_by_id(self.user_id)

        self.assertIsInstance(result, UserEntity)
        self.assertEqual(result.id, self.user_id)
        self.assertEqual(result.email, self.user_email)

    def test_get_by_id_non_existing_user(self):
        """Test obtener usuario que no existe"""
        non_existing_id = str(uuid4())
        result = self.repository.get_by_id(non_existing_id)

        self.assertIsNone(result)

    def test_get_by_email_existing_user(self):
        """Test obtener usuario por email"""
        result = self.repository.get_by_email(self.user_email)

        self.assertIsInstance(result, UserEntity)
        self.assertEqual(result.email, self.user_email)

    def test_get_by_email_non_existing_user(self):
        """Test obtener usuario por email que no existe"""
        result = self.repository.get_by_email("nonexisting@example.com")

        self.assertIsNone(result)

    def test_get_all_users(self):
        """Test obtener todos los usuarios"""
        # Crear un segundo usuario
        UserProfile.objects.create(id=str(uuid4()), email="test2@example.com")

        result = self.repository.get_all()

        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 2)
        self.assertTrue(all(isinstance(user, UserEntity) for user in result))

    def test_save_new_user(self):
        """Test guardar nuevo usuario"""
        new_user = UserEntity(
            id=str(uuid4()), email="new@example.com", profile_picture=None
        )

        result = self.repository.save(new_user)

        self.assertIsInstance(result, UserEntity)
        self.assertEqual(result.email, "new@example.com")

        # Verificar que se guardó en la BD
        saved_model = UserProfile.objects.get(email="new@example.com")
        self.assertEqual(saved_model.email, "new@example.com")

    def test_update_user(self):
        """Test actualizar usuario existente"""
        updated_user = UserEntity(
            id=self.user_id,
            email=self.user_email,
            profile_picture="https://example.com/new_picture.jpg",
        )

        result = self.repository.update(self.user_id, updated_user)

        self.assertEqual(result.profile_picture, "https://example.com/new_picture.jpg")

        # Verificar que se actualizó en la BD
        updated_model = UserProfile.objects.get(id=self.user_id)
        self.assertEqual(
            updated_model.profile_picture, "https://example.com/new_picture.jpg"
        )

    def test_delete_user(self):
        """Test eliminar usuario"""
        self.repository.delete(self.user_id)

        # Verificar que se eliminó de la BD
        with self.assertRaises(UserProfile.DoesNotExist):
            UserProfile.objects.get(id=self.user_id)


if __name__ == "__main__":
    import django

    django.setup()
    unittest.main()
