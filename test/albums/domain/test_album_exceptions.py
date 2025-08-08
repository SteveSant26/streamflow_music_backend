"""
Tests para excepciones del dominio de Albums.
Valida el comportamiento de las excepciones personalizadas del módulo albums.
"""

import pytest
from apps.albums.domain.exceptions import (
    AlbumNotFoundException,
    AlbumCreationException,
    AlbumUpdateException
)
from src.common.exceptions import DomainException, NotFoundException


class TestAlbumNotFoundException:
    """Tests para AlbumNotFoundException"""
    
    def test_album_not_found_exception_creation(self):
        """Test que verifica la creación de AlbumNotFoundException."""
        album_id = "test-album-123"
        
        exception = AlbumNotFoundException(album_id)
        
        assert exception.message == f"Album con ID {album_id} no encontrado."
        assert exception.code == 404
        assert exception.identifier == "not_found_error"
        
        # Verificar que str() devuelve el diccionario serializado
        expected_error_dict = {"not_found_error": [f"Album con ID {album_id} no encontrado."]}
        assert str(exception) == str(expected_error_dict)
        
    def test_album_not_found_exception_with_different_ids(self):
        """Test que valida AlbumNotFoundException con diferentes IDs"""
        test_cases = [
            "album-001",
            "spotify:album:123abc", 
            "youtube:album:xyz789",
            "",
            "12345"
        ]
        
        for album_id in test_cases:
            exception = AlbumNotFoundException(album_id)
            expected_message = f"Album con ID {album_id} no encontrado."
            expected_error_dict = {"not_found_error": [expected_message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_album_not_found_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = AlbumNotFoundException("test-id")
        
        assert isinstance(exception, AlbumNotFoundException)
        assert isinstance(exception, NotFoundException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestAlbumCreationException:
    """Tests para AlbumCreationException"""
    
    def test_album_creation_exception_creation(self):
        """Test que valida la creación de AlbumCreationException"""
        message = "Error al crear el álbum"
        exception = AlbumCreationException(message)
        
        assert isinstance(exception, DomainException)
        expected_error_dict = {"domain_error": [message]}
        assert str(exception) == str(expected_error_dict)
        
    def test_album_creation_exception_with_different_messages(self):
        """Test que valida AlbumCreationException con diferentes mensajes"""
        test_messages = [
            "Error al crear el álbum",
            "Álbum duplicado encontrado",
            "Datos de álbum inválidos", 
            "Error de conexión con servicio externo",
            "",
            "Error crítico: no se pudo procesar la solicitud"
        ]
        
        for message in test_messages:
            exception = AlbumCreationException(message)
            expected_error_dict = {"domain_error": [message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_album_creation_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = AlbumCreationException("test message")
        
        assert isinstance(exception, AlbumCreationException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestAlbumUpdateException:
    """Tests para AlbumUpdateException"""
    
    def test_album_update_exception_creation(self):
        """Test que valida la creación de AlbumUpdateException"""
        message = "Error al actualizar el álbum"
        exception = AlbumUpdateException(message)
        
        assert isinstance(exception, DomainException)
        expected_error_dict = {"domain_error": [message]}
        assert str(exception) == str(expected_error_dict)
        
    def test_album_update_exception_with_different_messages(self):
        """Test que valida AlbumUpdateException con diferentes mensajes"""
        test_messages = [
            "Error al actualizar el álbum",
            "Álbum no encontrado para actualizar",
            "Datos de actualización inválidos",
            "Error de concurrencia en actualización",
            "",
            "Timeout en operación de actualización"
        ]
        
        for message in test_messages:
            exception = AlbumUpdateException(message)
            expected_error_dict = {"domain_error": [message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_album_update_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = AlbumUpdateException("test message")
        
        assert isinstance(exception, AlbumUpdateException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestExceptionsInteraction:
    """Tests para interacciones entre excepciones"""
    
    def test_exception_messages_are_preserved(self):
        """Test que valida que los mensajes se preservan correctamente"""
        album_id = "album-123"
        expected_message = f"Album con ID {album_id} no encontrado."
        
        exception = AlbumNotFoundException(album_id)
        expected_error_dict = {"not_found_error": [expected_message]}
        
        assert str(exception) == str(expected_error_dict)
        assert exception.message == expected_message
        
    def test_different_exception_types_have_different_identifiers(self):
        """Test que valida que diferentes excepciones tienen identificadores únicos"""
        album_id = "test-album"
        message = "Error genérico"
        
        not_found = AlbumNotFoundException(album_id)
        creation_error = AlbumCreationException(message)
        update_error = AlbumUpdateException(message)
        
        assert not_found.identifier == "not_found_error"
        assert creation_error.identifier == "domain_error"
        assert update_error.identifier == "domain_error"
        
    def test_exceptions_are_different_instances(self):
        """Test que valida que las excepciones son instancias diferentes"""
        album_id = "test-album"
        message = "Error genérico"
        
        exception1 = AlbumNotFoundException(album_id)
        exception2 = AlbumCreationException(message)
        exception3 = AlbumUpdateException(message)
        
        assert exception1 is not exception2
        assert exception2 is not exception3
        assert exception1 is not exception3
        
        assert type(exception1) != type(exception2)
        assert type(exception2) != type(exception3)
        assert type(exception1) != type(exception3)
