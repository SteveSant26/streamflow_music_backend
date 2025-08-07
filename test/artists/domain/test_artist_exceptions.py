"""
Tests para excepciones del dominio de Artists.
Valida el comportamiento de las excepciones personalizadas del módulo artists.
"""

import pytest
from src.apps.artists.domain.exceptions import (
    ArtistNotFoundException,
    ArtistCreationException,
    ArtistUpdateException
)
from src.common.exceptions import DomainException, NotFoundException


class TestArtistNotFoundException:
    """Tests para ArtistNotFoundException"""
    
    def test_artist_not_found_exception_creation(self):
        """Test que verifica la creación de ArtistNotFoundException."""
        artist_id = "test-artist-123"
        
        exception = ArtistNotFoundException(artist_id)
        
        assert exception.message == f"Artist con ID {artist_id} no encontrado."
        assert exception.code == 404
        assert exception.identifier == "not_found_error"
        
        # Verificar que str() devuelve el diccionario serializado
        expected_error_dict = {"not_found_error": [f"Artist con ID {artist_id} no encontrado."]}
        assert str(exception) == str(expected_error_dict)
        
    def test_artist_not_found_exception_with_different_ids(self):
        """Test que valida ArtistNotFoundException con diferentes IDs"""
        test_cases = [
            "artist-001",
            "spotify:artist:123abc",
            "youtube:artist:xyz789",
            "",
            "12345"
        ]
        
        for artist_id in test_cases:
            exception = ArtistNotFoundException(artist_id)
            expected_message = f"Artist con ID {artist_id} no encontrado."
            expected_error_dict = {"not_found_error": [expected_message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_artist_not_found_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = ArtistNotFoundException("test-id")
        
        assert isinstance(exception, ArtistNotFoundException)
        assert isinstance(exception, NotFoundException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestArtistCreationException:
    """Tests para ArtistCreationException"""
    
    def test_artist_creation_exception_creation(self):
        """Test que valida la creación de ArtistCreationException"""
        message = "Error al crear el artista"
        exception = ArtistCreationException(message)
        
        assert isinstance(exception, DomainException)
        expected_error_dict = {"domain_error": [message]}
        assert str(exception) == str(expected_error_dict)
        
    def test_artist_creation_exception_with_different_messages(self):
        """Test que valida ArtistCreationException con diferentes mensajes"""
        test_messages = [
            "Error al crear el artista",
            "Artista duplicado encontrado",
            "Datos de artista inválidos",
            "Error de conexión con servicio externo",
            "",
            "Error crítico: no se pudo procesar la solicitud"
        ]
        
        for message in test_messages:
            exception = ArtistCreationException(message)
            expected_error_dict = {"domain_error": [message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_artist_creation_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = ArtistCreationException("test message")
        
        assert isinstance(exception, ArtistCreationException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestArtistUpdateException:
    """Tests para ArtistUpdateException"""
    
    def test_artist_update_exception_creation(self):
        """Test que valida la creación de ArtistUpdateException"""
        message = "Error al actualizar el artista"
        exception = ArtistUpdateException(message)
        
        assert isinstance(exception, DomainException)
        expected_error_dict = {"domain_error": [message]}
        assert str(exception) == str(expected_error_dict)
        
    def test_artist_update_exception_with_different_messages(self):
        """Test que valida ArtistUpdateException con diferentes mensajes"""
        test_messages = [
            "Error al actualizar el artista",
            "Artista no encontrado para actualizar",
            "Datos de actualización inválidos",
            "Error de concurrencia en actualización",
            "",
            "Timeout en operación de actualización"
        ]
        
        for message in test_messages:
            exception = ArtistUpdateException(message)
            expected_error_dict = {"domain_error": [message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_artist_update_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = ArtistUpdateException("test message")
        
        assert isinstance(exception, ArtistUpdateException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestArtistExceptionsInteraction:
    """Tests para interacciones entre excepciones"""
    
    def test_exception_messages_are_preserved(self):
        """Test que valida que los mensajes se preservan correctamente"""
        artist_id = "artist-123"
        expected_message = f"Artist con ID {artist_id} no encontrado."
        
        exception = ArtistNotFoundException(artist_id)
        expected_error_dict = {"not_found_error": [expected_message]}
        
        assert str(exception) == str(expected_error_dict)
        assert exception.message == expected_message
        
    def test_different_exception_types_have_different_identifiers(self):
        """Test que valida que diferentes excepciones tienen identificadores únicos"""
        artist_id = "test-artist"
        message = "Error genérico"
        
        not_found = ArtistNotFoundException(artist_id)
        creation_error = ArtistCreationException(message)
        update_error = ArtistUpdateException(message)
        
        assert not_found.identifier == "not_found_error"
        assert creation_error.identifier == "domain_error"
        assert update_error.identifier == "domain_error"
        
    def test_exceptions_are_different_instances(self):
        """Test que valida que las excepciones son instancias diferentes"""
        artist_id = "test-artist"
        message = "Error genérico"
        
        exception1 = ArtistNotFoundException(artist_id)
        exception2 = ArtistCreationException(message)
        exception3 = ArtistUpdateException(message)
        
        assert exception1 is not exception2
        assert exception2 is not exception3
        assert exception1 is not exception3
        
        assert type(exception1) != type(exception2)
        assert type(exception2) != type(exception3)
        assert type(exception1) != type(exception3)
