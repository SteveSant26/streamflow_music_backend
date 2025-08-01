"""
Tests para la API de user_profile
"""
from uuid import uuid4

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.user_profile.infrastructure.models.user_profile import UserProfileModel


@override_settings(
    ROOT_URLCONF="config.urls_test",
    USE_TZ=True,
    USE_I18N=True,
)
class TestUserProfileAPI(TestCase):
    """Test cases para la API de UserProfile"""

    def setUp(self):
        """Setup que se ejecuta antes de cada test"""
        self.client = APIClient()
        self.user_id = str(uuid4())
        self.user_email = "test@example.com"

        # Crear usuario de prueba
        self.user_profile = UserProfileModel.objects.create(
            id=self.user_id, email=self.user_email, profile_picture=None
        )

    def test_get_user_profile_success(self):
        """Test obtener perfil de usuario exitosamente"""
        url = reverse("userprofile-detail", kwargs={"pk": self.user_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["email"], self.user_email)
        self.assertIn("id", data)

    def test_get_user_profile_not_found(self):
        """Test obtener perfil que no existe"""
        non_existing_id = str(uuid4())
        url = reverse("userprofile-detail", kwargs={"pk": non_existing_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_user_profiles(self):
        """Test listar todos los perfiles"""
        # Crear otro usuario
        UserProfileModel.objects.create(id=str(uuid4()), email="test2@example.com")

        url = reverse("userprofile-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertGreaterEqual(len(data), 2)

    def test_create_user_profile(self):
        """Test crear nuevo perfil de usuario"""
        url = reverse("userprofile-list")
        data = {"id": str(uuid4()), "email": "new@example.com", "profile_picture": None}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = UserProfileModel.objects.get(email="new@example.com")
        self.assertEqual(created_user.email, "new@example.com")

    def test_update_user_profile(self):
        """Test actualizar perfil de usuario"""
        url = reverse("userprofile-detail", kwargs={"pk": self.user_id})
        data = {"profile_picture": "https://example.com/new_picture.jpg"}

        response = self.client.patch(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = UserProfileModel.objects.get(id=self.user_id)
        self.assertEqual(
            updated_user.profile_picture, "https://example.com/new_picture.jpg"
        )

    def test_delete_user_profile(self):
        """Test eliminar perfil de usuario"""
        url = reverse("userprofile-detail", kwargs={"pk": self.user_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verificar que se eliminó
        with self.assertRaises(UserProfileModel.DoesNotExist):
            UserProfileModel.objects.get(id=self.user_id)


if __name__ == "__main__":
    import django

    django.setup()
    import unittest

    unittest.main()
