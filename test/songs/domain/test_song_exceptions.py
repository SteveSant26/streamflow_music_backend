"""
Tests para excepciones del dominio de Songs.
Valida el comportamiento de las excepciones personalizadas del módulo songs.
"""

import pytest
from apps.songs.domain.exceptions import (
    SongNotFoundException,
    SongCreationException,
    SongUpdateException,
    SongPlayCountException
)
from common.exceptions import DomainException, NotFoundException


class TestSongNotFoundException:
    """Tests para SongNotFoundException"""
    
    def test_song_not_found_exception_creation(self):
        """Test que verifica la creación de SongNotFoundException."""
        song_id = "test-song-123"
        
        exception = SongNotFoundException(song_id)
        
        assert exception.message == f"Song con ID {song_id} no encontrado."
        assert exception.code == 404
        assert exception.identifier == "not_found_error"
        
        # Verificar que str() devuelve el diccionario serializado
        expected_error_dict = {"not_found_error": [f"Song con ID {song_id} no encontrado."]}
        assert str(exception) == str(expected_error_dict)
        
    def test_song_not_found_exception_with_different_ids(self):
        """Test que valida SongNotFoundException con diferentes IDs"""
        test_cases = [
            "song-001",
            "spotify:song:123abc",
            "youtube:song:xyz789",
            "",
            "12345"
        ]
        
        for song_id in test_cases:
            exception = SongNotFoundException(song_id)
            expected_message = f"Song con ID {song_id} no encontrado."
            expected_error_dict = {"not_found_error": [expected_message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_song_not_found_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = SongNotFoundException("test-id")
        
        assert isinstance(exception, SongNotFoundException)
        assert isinstance(exception, NotFoundException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestSongCreationException:
    """Tests para SongCreationException"""
    
    def test_song_creation_exception_creation(self):
        """Test que valida la creación de SongCreationException"""
        message = "Error al crear la canción"
        exception = SongCreationException(message)
        
        assert isinstance(exception, DomainException)
        expected_error_dict = {"domain_error": [message]}
        assert str(exception) == str(expected_error_dict)
        
    def test_song_creation_exception_with_different_messages(self):
        """Test que valida SongCreationException con diferentes mensajes"""
        test_messages = [
            "Error al crear la canción",
            "Canción duplicada encontrada",
            "Datos de canción inválidos",
            "Error de conexión con servicio externo",
            "",
            "Error crítico: no se pudo procesar la solicitud"
        ]
        
        for message in test_messages:
            exception = SongCreationException(message)
            expected_error_dict = {"domain_error": [message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_song_creation_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = SongCreationException("test message")
        
        assert isinstance(exception, SongCreationException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestSongUpdateException:
    """Tests para SongUpdateException"""
    
    def test_song_update_exception_creation(self):
        """Test que valida la creación de SongUpdateException"""
        message = "Error al actualizar la canción"
        exception = SongUpdateException(message)
        
        assert isinstance(exception, DomainException)
        expected_error_dict = {"domain_error": [message]}
        assert str(exception) == str(expected_error_dict)
        
    def test_song_update_exception_with_different_messages(self):
        """Test que valida SongUpdateException con diferentes mensajes"""
        test_messages = [
            "Error al actualizar la canción",
            "Canción no encontrada para actualizar",
            "Datos de actualización inválidos",
            "Error de concurrencia en actualización",
            "",
            "Timeout en operación de actualización"
        ]
        
        for message in test_messages:
            exception = SongUpdateException(message)
            expected_error_dict = {"domain_error": [message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_song_update_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = SongUpdateException("test message")
        
        assert isinstance(exception, SongUpdateException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestSongPlayCountException:
    """Tests para SongPlayCountException"""
    
    def test_song_play_count_exception_creation(self):
        """Test que valida la creación de SongPlayCountException"""
        message = "Error al actualizar contador de reproducciones"
        exception = SongPlayCountException(message)
        
        assert isinstance(exception, DomainException)
        expected_error_dict = {"domain_error": [message]}
        assert str(exception) == str(expected_error_dict)
        
    def test_song_play_count_exception_with_different_messages(self):
        """Test que valida SongPlayCountException con diferentes mensajes"""
        test_messages = [
            "Error al actualizar contador de reproducciones",
            "Canción no encontrada para actualizar contador",
            "Contador de reproducciones inválido",
            "Error de base de datos al actualizar contador",
            "",
            "Timeout en actualización de contador"
        ]
        
        for message in test_messages:
            exception = SongPlayCountException(message)
            expected_error_dict = {"domain_error": [message]}
            assert str(exception) == str(expected_error_dict)
            
    def test_song_play_count_exception_inheritance(self):
        """Test que valida la jerarquía de herencia"""
        exception = SongPlayCountException("test message")
        
        assert isinstance(exception, SongPlayCountException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)


class TestSongExceptionsInteraction:
    """Tests para interacciones entre excepciones"""
    
    def test_exception_messages_are_preserved(self):
        """Test que valida que los mensajes se preservan correctamente"""
        song_id = "song-123"
        expected_message = f"Song con ID {song_id} no encontrado."
        
        exception = SongNotFoundException(song_id)
        expected_error_dict = {"not_found_error": [expected_message]}
        
        assert str(exception) == str(expected_error_dict)
        assert exception.message == expected_message
        
    def test_different_exception_types_have_different_identifiers(self):
        """Test que valida que diferentes excepciones tienen identificadores únicos"""
        song_id = "test-song"
        message = "Error genérico"
        
        not_found = SongNotFoundException(song_id)
        creation_error = SongCreationException(message)
        update_error = SongUpdateException(message)
        play_count_error = SongPlayCountException(message)
        
        assert not_found.identifier == "not_found_error"
        assert creation_error.identifier == "domain_error"
        assert update_error.identifier == "domain_error"
        assert play_count_error.identifier == "domain_error"
        
    def test_exceptions_are_different_instances(self):
        """Test que valida que las excepciones son instancias diferentes"""
        song_id = "test-song"
        message = "Error genérico"
        
        exception1 = SongNotFoundException(song_id)
        exception2 = SongCreationException(message)
        exception3 = SongUpdateException(message)
        exception4 = SongPlayCountException(message)
        
        assert exception1 is not exception2
        assert exception2 is not exception3
        assert exception3 is not exception4
        assert exception1 is not exception4
        
        assert type(exception1) != type(exception2)
        assert type(exception2) != type(exception3)
        assert type(exception3) != type(exception4)
        assert type(exception1) != type(exception4)
