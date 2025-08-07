import pytest
from src.apps.user_profile.domain.exceptions import (
    UserNotFoundException,
    UserProfilePictureUploadException
)


class TestUserProfileExceptions:
    """Test suite para excepciones de User Profile"""

    def test_user_not_found_exception_creation(self):
        """Test creación de UserNotFoundException"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        exception = UserNotFoundException(user_id)
        
        assert exception.message == f"User con ID {user_id} no encontrado."
        # Las excepciones retornan dict en str(), no el mensaje directo
        assert "User con ID" in str(exception)
        assert user_id in str(exception)

    def test_user_not_found_exception_message_content(self):
        """Test contenido del mensaje de UserNotFoundException"""
        user_id = "test-user-id"
        exception = UserNotFoundException(user_id)
        
        assert hasattr(exception, 'message')
        assert exception.message == f"User con ID {user_id} no encontrado."

    def test_user_profile_picture_upload_exception_creation(self):
        """Test creación de UserProfilePictureUploadException"""
        message = "Error al subir imagen de perfil"
        exception = UserProfilePictureUploadException(message)
        
        assert exception.message == message
        # Las excepciones retornan dict en str(), no el mensaje directo  
        assert message in str(exception)

    def test_user_profile_picture_upload_exception_message_content(self):
        """Test contenido del mensaje de UserProfilePictureUploadException"""
        message = "No se pudo procesar la imagen"
        exception = UserProfilePictureUploadException(message)
        
        assert hasattr(exception, 'message')
        assert exception.message == message

    def test_user_not_found_exception_different_ids(self):
        """Test UserNotFoundException con diferentes IDs produce diferentes mensajes"""
        user_id_1 = "user-1"
        user_id_2 = "user-2"
        
        exception_1 = UserNotFoundException(user_id_1)
        exception_2 = UserNotFoundException(user_id_2)
        
        assert exception_1.message != exception_2.message
        assert user_id_1 in exception_1.message
        assert user_id_2 in exception_2.message

    def test_user_profile_picture_upload_exception_different_messages(self):
        """Test UserProfilePictureUploadException con diferentes mensajes"""
        message_1 = "Error de formato"
        message_2 = "Error de tamaño"
        
        exception_1 = UserProfilePictureUploadException(message_1)
        exception_2 = UserProfilePictureUploadException(message_2)
        
        assert exception_1.message != exception_2.message
        assert exception_1.message == message_1
        assert exception_2.message == message_2

    def test_user_not_found_exception_empty_id(self):
        """Test UserNotFoundException con ID vacío"""
        user_id = ""
        exception = UserNotFoundException(user_id)
        
        assert exception.message == f"User con ID {user_id} no encontrado."
        assert "User con ID" in str(exception)
        assert "no encontrado" in str(exception)

    def test_user_profile_picture_upload_exception_empty_message(self):
        """Test UserProfilePictureUploadException con mensaje vacío"""
        message = ""
        exception = UserProfilePictureUploadException(message)
        
        assert exception.message == message
        assert hasattr(exception, 'message')
