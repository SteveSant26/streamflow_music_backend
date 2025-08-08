"""
Tests para las excepciones del dominio de playlists
"""

import pytest
from src.apps.playlists.domain.exceptions import (
    PlaylistNotFoundException,
    PlaylistValidationException,
    PlaylistPermissionException,
    PlaylistSongNotFoundException,
    PlaylistSongAlreadyExistsException,
    PlaylistImageUploadException
)
from src.common.exceptions import DomainException, NotFoundException


"""
Tests para las excepciones del dominio de playlists
"""

import pytest
from src.apps.playlists.domain.exceptions import (
    PlaylistNotFoundException,
    PlaylistValidationException,
    PlaylistPermissionException,
    PlaylistSongNotFoundException,
    PlaylistSongAlreadyExistsException,
    PlaylistImageUploadException
)
from src.common.exceptions import DomainException, NotFoundException


class TestPlaylistExceptions:
    """Tests para las excepciones del dominio de playlists"""

    def test_playlist_not_found_exception(self):
        """Test excepción PlaylistNotFoundException"""
        message = "La playlist con ID playlist-123 no fue encontrada"
        exception = PlaylistNotFoundException(message)
        
        assert str(exception) == str({"not_found_error": [message]})
        assert exception.message == message
        assert exception.code == 404
        assert exception.identifier == "not_found_error"
        
        # Test que hereda de NotFoundException y DomainException
        assert isinstance(exception, NotFoundException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)

    def test_playlist_validation_exception(self):
        """Test excepción PlaylistValidationException"""
        message = "El nombre de la playlist es requerido"
        exception = PlaylistValidationException(message)
        
        assert str(exception) == str({"domain_error": [message]})
        assert exception.message == message
        assert exception.code == 500
        assert exception.identifier == "domain_error"
        
        # Test que hereda de DomainException
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)

    def test_playlist_permission_exception(self):
        """Test excepción PlaylistPermissionException"""
        message = "El usuario no tiene permisos para acceder a esta playlist"
        exception = PlaylistPermissionException(message)
        
        assert str(exception) == str({"domain_error": [message]})
        assert exception.message == message
        assert exception.code == 500
        assert exception.identifier == "domain_error"
        
        # Test que hereda de DomainException
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)

    def test_playlist_song_not_found_exception(self):
        """Test excepción PlaylistSongNotFoundException"""
        message = "La canción no se encuentra en la playlist"
        exception = PlaylistSongNotFoundException(message)
        
        assert str(exception) == str({"not_found_error": [message]})
        assert exception.message == message
        assert exception.code == 404
        assert exception.identifier == "not_found_error"
        
        # Test que hereda de NotFoundException y DomainException
        assert isinstance(exception, NotFoundException)
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)

    def test_playlist_song_already_exists_exception(self):
        """Test excepción PlaylistSongAlreadyExistsException"""
        message = "La canción ya existe en la playlist"
        exception = PlaylistSongAlreadyExistsException(message)
        
        assert str(exception) == str({"domain_error": [message]})
        assert exception.message == message
        assert exception.code == 500
        assert exception.identifier == "domain_error"
        
        # Test que hereda de DomainException
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)

    def test_playlist_image_upload_exception(self):
        """Test excepción PlaylistImageUploadException"""
        message = "Error al subir la imagen de la playlist"
        exception = PlaylistImageUploadException(message)
        
        assert str(exception) == str({"domain_error": [message]})
        assert exception.message == message
        assert exception.code == 500
        assert exception.identifier == "domain_error"
        
        # Test que hereda de DomainException
        assert isinstance(exception, DomainException)
        assert isinstance(exception, Exception)

    def test_exception_with_custom_code(self):
        """Test excepción con código personalizado"""
        message = "Error de permisos"
        exception = PlaylistPermissionException(message, code=403)
        
        assert exception.message == message
        assert exception.code == 403
        assert exception.identifier == "domain_error"

    def test_exception_with_details(self):
        """Test excepción con detalles adicionales"""
        message = "Error de validación"
        details = {"field": "name", "value": "", "constraint": "not_empty"}
        exception = PlaylistValidationException(message, details=details)
        
        assert exception.message == message
        assert exception.details == details
        assert exception.code == 500

    def test_not_found_exceptions_inherit_correctly(self):
        """Test que las excepciones NotFound heredan correctamente"""
        not_found_exceptions = [
            PlaylistNotFoundException("test"),
            PlaylistSongNotFoundException("test")
        ]
        
        for exception in not_found_exceptions:
            assert isinstance(exception, NotFoundException)
            assert isinstance(exception, DomainException)
            assert isinstance(exception, Exception)
            assert exception.code == 404
            assert exception.identifier == "not_found_error"

    def test_domain_exceptions_inherit_correctly(self):
        """Test que las excepciones de dominio heredan correctamente"""
        domain_exceptions = [
            PlaylistValidationException("test"),
            PlaylistPermissionException("test"),
            PlaylistSongAlreadyExistsException("test"),
            PlaylistImageUploadException("test")
        ]
        
        for exception in domain_exceptions:
            assert isinstance(exception, DomainException)
            assert isinstance(exception, Exception)
            assert exception.code == 500
            assert exception.identifier == "domain_error"

    def test_exceptions_can_be_raised_and_caught(self):
        """Test que las excepciones pueden ser lanzadas y capturadas"""
        # Test excepción específica
        with pytest.raises(PlaylistNotFoundException):
            raise PlaylistNotFoundException("Playlist no encontrada")

        # Test captura por clase base NotFoundException
        with pytest.raises(NotFoundException):
            raise PlaylistSongNotFoundException("Canción no encontrada en playlist")

        # Test captura por clase base DomainException
        with pytest.raises(DomainException):
            raise PlaylistValidationException("Error de validación")

        # Test captura general
        with pytest.raises(Exception):
            raise PlaylistImageUploadException("Error subiendo imagen")

    def test_all_exceptions_with_different_messages(self):
        """Test todas las excepciones con diferentes mensajes"""
        test_cases = [
            (PlaylistNotFoundException, "Playlist específica no encontrada"),
            (PlaylistValidationException, "Nombre de playlist inválido"),
            (PlaylistPermissionException, "Sin permisos de escritura"),
            (PlaylistSongNotFoundException, "Canción removida de la playlist"),
            (PlaylistSongAlreadyExistsException, "Canción duplicada en playlist"),
            (PlaylistImageUploadException, "Formato de imagen no soportado")
        ]
        
        for exception_class, message in test_cases:
            exception = exception_class(message)
            assert exception.message == message
            assert isinstance(exception, Exception)

    def test_exception_serialization_format(self):
        """Test formato de serialización de excepciones"""
        # NotFoundException format
        not_found = PlaylistNotFoundException("Resource not found")
        assert "not_found_error" in str(not_found)
        
        # DomainException format
        domain_error = PlaylistValidationException("Validation failed")
        assert "domain_error" in str(domain_error)
