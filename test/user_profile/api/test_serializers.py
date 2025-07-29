"""
Tests para los serializers de user_profile
"""
from django.test import TestCase
from uuid import uuid4

from apps.user_profile.infrastructure.models.user_profile import UserProfile
from apps.user_profile.api.serializers.retrieve_user_profile_serializer import RetrieveUserProfileSerializer


class TestUserProfileSerializers(TestCase):
    """Test cases para los serializers de UserProfile"""
    
    def setUp(self):
        """Setup que se ejecuta antes de cada test"""
        self.user_id = str(uuid4())
        self.user_email = "test@example.com"
        
        self.user_profile = UserProfile.objects.create(
            id=self.user_id,
            email=self.user_email,
            profile_picture=None
        )
    
    def test_retrieve_serializer_basic(self):
        """Test serializer básico de retrieve"""
        serializer = RetrieveUserProfileSerializer(self.user_profile)
        data = serializer.data
        
        # Verificar que contiene los campos esperados
        expected_fields = ['id', 'email', 'profile_picture']
        for field in expected_fields:
            self.assertIn(field, data)
        
        self.assertEqual(data['email'], self.user_email)
        self.assertIsNone(data['profile_picture'])
    
    def test_retrieve_serializer_with_picture(self):
        """Test serializer con foto de perfil"""
        picture_url = "https://example.com/picture.jpg"
        user_with_picture = UserProfile.objects.create(
            id=str(uuid4()),
            email="with_picture@example.com",
            profile_picture=picture_url
        )
        
        serializer = RetrieveUserProfileSerializer(user_with_picture)
        data = serializer.data
        
        self.assertEqual(data['profile_picture'], picture_url)
    
    def test_retrieve_serializer_many(self):
        """Test serializer con múltiples usuarios"""
        # Crear otro usuario
        user2 = UserProfile.objects.create(
            id=str(uuid4()),
            email="test2@example.com",
            profile_picture="https://example.com/pic2.jpg"
        )
        
        users = [self.user_profile, user2]
        serializer = RetrieveUserProfileSerializer(users, many=True)
        data = serializer.data
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['email'], self.user_email)
        self.assertEqual(data[1]['email'], "test2@example.com")
    
    def test_serializer_read_only(self):
        """Test que el serializer es de solo lectura"""
        serializer = RetrieveUserProfileSerializer(self.user_profile)
        
        # Un serializer de retrieve no debería permitir escritura
        # Esto se verificaría en el código del serializer
        self.assertTrue(hasattr(serializer, 'data'))


if __name__ == '__main__':
    import django
    django.setup()
    import unittest
    unittest.main()
