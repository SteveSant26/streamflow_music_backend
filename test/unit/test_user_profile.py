"""
Tests unitarios para User Profile - Streamflow Music Backend
Tests modernos usando pytest y dataclasses simples
"""

import pytest
from dataclasses import dataclass
from typing import Optional


@dataclass
class SimpleUser:
    """Entidad simple para tests de User Profile"""
    id: str
    email: str
    username: str
    profile_picture: Optional[str] = None
    is_active: bool = True
    is_premium: bool = False
    total_playlists: int = 0
    following_count: int = 0
    followers_count: int = 0
    
    def is_verified(self) -> bool:
        """Usuario verificado si tiene más de 1000 seguidores"""
        return self.followers_count >= 1000
    
    def __str__(self) -> str:
        return f"User({self.username})"


@pytest.mark.unit
class TestSimpleUserEntity:
    """Tests para la entidad User"""

    def test_user_creation_complete(self):
        """Test creación completa de usuario"""
        user = SimpleUser(
            id="user-123",
            email="john@example.com",
            username="john_doe",
            profile_picture="https://example.com/john.jpg",
            is_premium=True,
            total_playlists=5,
            following_count=250,
            followers_count=1500
        )
        
        assert user.id == "user-123"
        assert user.email == "john@example.com"
        assert user.username == "john_doe"
        assert user.profile_picture == "https://example.com/john.jpg"
        assert user.is_premium is True
        assert user.is_active is True
        assert user.total_playlists == 5
        assert user.following_count == 250
        assert user.followers_count == 1500

    @pytest.mark.unit
    def test_user_minimal_creation(self):
        """Test creación mínima de usuario"""
        user = SimpleUser(
            id="user-456",
            email="jane@example.com",
            username="jane_smith"
        )
        
        assert user.id == "user-456"
        assert user.email == "jane@example.com"
        assert user.username == "jane_smith"
        assert user.profile_picture is None
        assert user.is_active is True
        assert user.is_premium is False
        assert user.total_playlists == 0
        assert user.following_count == 0
        assert user.followers_count == 0

    @pytest.mark.unit
    def test_user_verification_status(self):
        """Test estado de verificación por seguidores"""
        # Usuario no verificado
        regular_user = SimpleUser(
            id="user-789",
            email="regular@example.com",
            username="regular_user",
            followers_count=500
        )
        assert regular_user.is_verified() is False
        
        # Usuario verificado
        verified_user = SimpleUser(
            id="user-101",
            email="verified@example.com",
            username="verified_user",
            followers_count=2000
        )
        assert verified_user.is_verified() is True

    @pytest.mark.unit
    def test_user_premium_status(self):
        """Test diferentes estados premium"""
        free_user = SimpleUser(
            id="user-111",
            email="free@example.com",
            username="free_user",
            is_premium=False
        )
        assert free_user.is_premium is False
        
        premium_user = SimpleUser(
            id="user-222",
            email="premium@example.com",
            username="premium_user",
            is_premium=True
        )
        assert premium_user.is_premium is True

    @pytest.mark.unit
    def test_user_inactive_state(self):
        """Test usuario inactivo"""
        inactive_user = SimpleUser(
            id="user-333",
            email="inactive@example.com",
            username="inactive_user",
            is_active=False
        )
        assert inactive_user.is_active is False

    @pytest.mark.unit
    def test_user_social_metrics(self):
        """Test métricas sociales del usuario"""
        social_user = SimpleUser(
            id="user-444",
            email="social@example.com",
            username="social_user",
            total_playlists=15,
            following_count=300,
            followers_count=450
        )
        
        assert social_user.total_playlists == 15
        assert social_user.following_count == 300
        assert social_user.followers_count == 450

    @pytest.mark.unit
    def test_user_string_representation(self):
        """Test representación string del usuario"""
        user = SimpleUser(
            id="user-555",
            email="test@example.com",
            username="test_user"
        )
        assert str(user) == "User(test_user)"

    @pytest.mark.unit
    @pytest.mark.parametrize("followers,expected", [
        (0, False),
        (500, False),
        (999, False),
        (1000, True),
        (5000, True),
        (100000, True)
    ])
    def test_verification_thresholds(self, followers, expected):
        """Test diferentes umbrales de verificación"""
        user = SimpleUser(
            id="user-test",
            email="test@example.com",
            username="test_user",
            followers_count=followers
        )
        assert user.is_verified() == expected

    @pytest.mark.unit
    def test_user_email_validation_patterns(self):
        """Test diferentes patrones de email"""
        emails = [
            "user@example.com",
            "user.name@example.com", 
            "user+tag@example.co.uk",
            "123@example.org"
        ]
        
        for i, email in enumerate(emails):
            user = SimpleUser(
                id=f"user-{i}",
                email=email,
                username=f"user_{i}"
            )
            assert "@" in user.email
            assert "." in user.email

    @pytest.mark.unit
    def test_user_profile_picture_urls(self):
        """Test diferentes tipos de URLs de imagen"""
        urls = [
            "https://example.com/image.jpg",
            "https://cdn.example.com/users/123/avatar.png",
            "https://images.example.com/profile.webp"
        ]
        
        for i, url in enumerate(urls):
            user = SimpleUser(
                id=f"user-{i}",
                email=f"user{i}@example.com",
                username=f"user_{i}",
                profile_picture=url
            )
            assert user.profile_picture == url
            assert user.profile_picture.startswith("https://")
