import pytest
from src.common.exceptions import NotFoundException, DomainException
from src.apps.genres.domain.exceptions import (
    GenreNotFoundException,
    GenreCreationException,
    GenreUpdateException,
    GenreSearchException
)


class TestGenreExceptions:
    """Test suite para excepciones de Genres"""

    def test_genre_not_found_exception_creation(self):
        """Test creación de GenreNotFoundException"""
        genre_id = "rock-123"
        exception = GenreNotFoundException(genre_id)
        
        assert isinstance(exception, NotFoundException)
        assert isinstance(exception, GenreNotFoundException)
        # Las excepciones se serializan como diccionarios con ErrorDetail
        serialized = str(exception)
        assert f"Género con ID {genre_id} no encontrado." in serialized

    def test_genre_not_found_exception_serialization(self):
        """Test serialización de GenreNotFoundException"""
        genre_id = "jazz-456"
        exception = GenreNotFoundException(genre_id)
        
        # Las excepciones se serializan como diccionarios con ErrorDetail
        serialized = str(exception)
        assert isinstance(serialized, str)
        assert "not_found_error" in serialized
        assert f"Género con ID {genre_id} no encontrado." in serialized

    def test_genre_creation_exception_creation(self):
        """Test creación de GenreCreationException"""
        message = "Error al crear género"
        exception = GenreCreationException(message)
        
        assert isinstance(exception, DomainException)
        assert isinstance(exception, GenreCreationException)
        serialized = str(exception)
        assert message in serialized

    def test_genre_creation_exception_serialization(self):
        """Test serialización de GenreCreationException"""
        message = "Nombre del género ya existe"
        exception = GenreCreationException(message)
        
        # Las excepciones se serializan como diccionarios con ErrorDetail
        serialized = str(exception)
        assert isinstance(serialized, str)
        assert "domain_error" in serialized
        assert message in serialized

    def test_genre_update_exception_creation(self):
        """Test creación de GenreUpdateException"""
        message = "Error al actualizar género"
        exception = GenreUpdateException(message)
        
        assert isinstance(exception, DomainException)
        assert isinstance(exception, GenreUpdateException)
        serialized = str(exception)
        assert message in serialized

    def test_genre_update_exception_serialization(self):
        """Test serialización de GenreUpdateException"""
        message = "No se puede actualizar género inactivo"
        exception = GenreUpdateException(message)
        
        # Las excepciones se serializan como diccionarios con ErrorDetail
        serialized = str(exception)
        assert isinstance(serialized, str)
        assert "domain_error" in serialized
        assert message in serialized

    def test_genre_search_exception_creation_with_default_message(self):
        """Test creación de GenreSearchException con mensaje por defecto"""
        search_term = "rock alternativo"
        exception = GenreSearchException(search_term)
        
        assert isinstance(exception, DomainException)
        assert isinstance(exception, GenreSearchException)
        expected_message = f"Error en la búsqueda de géneros con término: {search_term}"
        serialized = str(exception)
        assert expected_message in serialized

    def test_genre_search_exception_creation_with_custom_message(self):
        """Test creación de GenreSearchException con mensaje personalizado"""
        search_term = "jazz"
        custom_message = "Servicio de búsqueda no disponible"
        exception = GenreSearchException(search_term, custom_message)
        
        serialized = str(exception)
        assert custom_message in serialized

    def test_genre_search_exception_serialization(self):
        """Test serialización de GenreSearchException"""
        search_term = "classical"
        exception = GenreSearchException(search_term)
        
        # Las excepciones se serializan como diccionarios con ErrorDetail
        serialized = str(exception)
        assert isinstance(serialized, str)
        assert "domain_error" in serialized
        assert f"Error en la búsqueda de géneros con término: {search_term}" in serialized

    def test_genre_not_found_exception_different_ids(self):
        """Test GenreNotFoundException con diferentes IDs produce diferentes mensajes"""
        genre_id_1 = "rock-1"
        genre_id_2 = "pop-2"
        
        exception_1 = GenreNotFoundException(genre_id_1)
        exception_2 = GenreNotFoundException(genre_id_2)
        
        assert exception_1.message != exception_2.message
        assert genre_id_1 in exception_1.message
        assert genre_id_2 in exception_2.message

    def test_genre_creation_exception_different_messages(self):
        """Test GenreCreationException con diferentes mensajes"""
        message_1 = "Error de validación"
        message_2 = "Error de base de datos"
        
        exception_1 = GenreCreationException(message_1)
        exception_2 = GenreCreationException(message_2)
        
        assert exception_1.message != exception_2.message
        assert exception_1.message == message_1
        assert exception_2.message == message_2

    def test_genre_update_exception_different_messages(self):
        """Test GenreUpdateException con diferentes mensajes"""
        message_1 = "Género no encontrado para actualizar"
        message_2 = "Permisos insuficientes para actualizar"
        
        exception_1 = GenreUpdateException(message_1)
        exception_2 = GenreUpdateException(message_2)
        
        assert exception_1.message != exception_2.message
        assert exception_1.message == message_1
        assert exception_2.message == message_2

    def test_genre_search_exception_empty_search_term(self):
        """Test GenreSearchException con término de búsqueda vacío"""
        search_term = ""
        exception = GenreSearchException(search_term)
        
        expected_message = f"Error en la búsqueda de géneros con término: {search_term}"
        serialized = str(exception)
        assert expected_message in serialized

    def test_genre_not_found_exception_empty_id(self):
        """Test GenreNotFoundException con ID vacío"""
        genre_id = ""
        exception = GenreNotFoundException(genre_id)
        
        serialized = str(exception)
        assert f"Género con ID  no encontrado." in serialized
