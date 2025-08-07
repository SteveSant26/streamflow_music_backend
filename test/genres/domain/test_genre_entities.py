import pytest
from datetime import datetime
from src.apps.genres.domain.entities import GenreEntity


class TestGenreEntity:
    """Test suite para GenreEntity"""

    def test_genre_entity_creation_minimal(self):
        """Test creación básica de GenreEntity con campos mínimos"""
        genre_id = "rock-genre-123"
        name = "Rock"
        
        entity = GenreEntity(
            id=genre_id,
            name=name
        )
        
        assert entity.id == genre_id
        assert entity.name == name
        assert entity.description is None
        assert entity.image_url is None
        assert entity.color_hex is None
        assert entity.popularity_score == 0
        assert entity.created_at is None
        assert entity.updated_at is None

    def test_genre_entity_creation_complete(self):
        """Test creación completa de GenreEntity con todos los campos"""
        genre_id = "jazz-genre-456"
        name = "Jazz"
        description = "Música jazz clásica"
        image_url = "https://example.com/jazz.jpg"
        color_hex = "#FF5733"
        popularity_score = 85
        created_at = datetime.now()
        updated_at = datetime.now()
        
        entity = GenreEntity(
            id=genre_id,
            name=name,
            description=description,
            image_url=image_url,
            color_hex=color_hex,
            popularity_score=popularity_score,
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert entity.id == genre_id
        assert entity.name == name
        assert entity.description == description
        assert entity.image_url == image_url
        assert entity.color_hex == color_hex
        assert entity.popularity_score == popularity_score
        assert entity.created_at == created_at
        assert entity.updated_at == updated_at

    def test_genre_entity_optional_fields_none(self):
        """Test GenreEntity con campos opcionales explícitamente None"""
        entity = GenreEntity(
            id="pop-123",
            name="Pop",
            description=None,
            image_url=None,
            color_hex=None,
            popularity_score=0,
            created_at=None,
            updated_at=None
        )
        
        assert entity.id == "pop-123"
        assert entity.name == "Pop"
        assert entity.description is None
        assert entity.image_url is None
        assert entity.color_hex is None
        assert entity.popularity_score == 0
        assert entity.created_at is None
        assert entity.updated_at is None

    def test_genre_entity_popularity_score_variations(self):
        """Test GenreEntity con diferentes scores de popularidad"""
        entity_low = GenreEntity(id="1", name="Genre1", popularity_score=10)
        entity_medium = GenreEntity(id="2", name="Genre2", popularity_score=50)
        entity_high = GenreEntity(id="3", name="Genre3", popularity_score=100)
        
        assert entity_low.popularity_score == 10
        assert entity_medium.popularity_score == 50
        assert entity_high.popularity_score == 100

    def test_genre_entity_string_fields(self):
        """Test que los campos string se mantengan como string"""
        entity = GenreEntity(
            id="string-test",
            name="Test Genre",
            description="A test description",
            image_url="test.jpg",
            color_hex="#FFFFFF"
        )
        
        assert isinstance(entity.id, str)
        assert isinstance(entity.name, str)
        assert isinstance(entity.description, str)
        assert isinstance(entity.image_url, str)
        assert isinstance(entity.color_hex, str)

    def test_genre_entity_equality(self):
        """Test igualdad entre entidades Genre"""
        created_time = datetime.now()
        
        entity1 = GenreEntity(
            id="test-id",
            name="Test",
            description="Test desc",
            image_url="test.jpg",
            color_hex="#123456",
            popularity_score=75,
            created_at=created_time,
            updated_at=created_time
        )
        
        entity2 = GenreEntity(
            id="test-id",
            name="Test",
            description="Test desc",
            image_url="test.jpg",
            color_hex="#123456",
            popularity_score=75,
            created_at=created_time,
            updated_at=created_time
        )
        
        assert entity1 == entity2

    def test_genre_entity_inequality(self):
        """Test desigualdad entre entidades Genre con diferentes IDs"""
        entity1 = GenreEntity(id="id-1", name="Genre1")
        entity2 = GenreEntity(id="id-2", name="Genre1")
        
        assert entity1 != entity2

    def test_genre_entity_datetime_fields(self):
        """Test campos datetime en GenreEntity"""
        created_at = datetime(2023, 1, 1, 12, 0, 0)
        updated_at = datetime(2023, 1, 2, 15, 30, 0)
        
        entity = GenreEntity(
            id="datetime-test",
            name="DateTime Test",
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert entity.created_at == created_at
        assert entity.updated_at == updated_at
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)
