import pytest
from src.apps.user_profile.domain.entities import UserProfileEntity


class TestUserProfileEntity:
    """Test suite para UserProfileEntity"""

    def test_user_profile_entity_creation(self):
        """Test creación básica de UserProfileEntity"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"
        profile_picture = "https://example.com/pic.jpg"
        
        entity = UserProfileEntity(
            id=user_id,
            email=email,
            profile_picture=profile_picture
        )
        
        assert entity.id == user_id
        assert entity.email == email
        assert entity.profile_picture == profile_picture

    def test_user_profile_entity_with_none_picture(self):
        """Test creación de UserProfileEntity con profile_picture None"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"
        
        entity = UserProfileEntity(
            id=user_id,
            email=email,
            profile_picture=None
        )
        
        assert entity.id == user_id
        assert entity.email == email
        assert entity.profile_picture is None

    def test_user_profile_entity_is_authenticated_property(self):
        """Test propiedad is_authenticated siempre True"""
        entity = UserProfileEntity(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            profile_picture=None
        )
        
        assert entity.is_authenticated is True

    def test_user_profile_entity_is_anonymous_property(self):
        """Test propiedad is_anonymous siempre False"""
        entity = UserProfileEntity(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com",
            profile_picture=None
        )
        
        assert entity.is_anonymous is False

    def test_user_profile_entity_string_representation(self):
        """Test que la entidad mantenga sus valores como string"""
        user_id = "test-id-123"
        email = "user@domain.com"
        profile_picture = "picture.png"
        
        entity = UserProfileEntity(
            id=user_id,
            email=email,
            profile_picture=profile_picture
        )
        
        assert isinstance(entity.id, str)
        assert isinstance(entity.email, str)
        assert isinstance(entity.profile_picture, str)

    def test_user_profile_entity_equality(self):
        """Test igualdad entre entidades UserProfile"""
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        email = "test@example.com"
        profile_picture = "pic.jpg"
        
        entity1 = UserProfileEntity(
            id=user_id,
            email=email,
            profile_picture=profile_picture
        )
        
        entity2 = UserProfileEntity(
            id=user_id,
            email=email,
            profile_picture=profile_picture
        )
        
        assert entity1 == entity2

    def test_user_profile_entity_inequality(self):
        """Test desigualdad entre entidades UserProfile con diferentes IDs"""
        email = "test@example.com"
        profile_picture = "pic.jpg"
        
        entity1 = UserProfileEntity(
            id="id-1",
            email=email,
            profile_picture=profile_picture
        )
        
        entity2 = UserProfileEntity(
            id="id-2",
            email=email,
            profile_picture=profile_picture
        )
        
        assert entity1 != entity2
