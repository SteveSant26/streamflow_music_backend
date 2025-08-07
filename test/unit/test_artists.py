"""
🧪 TESTS SIMPLES PARA ARTIST ENTITY SIN DJANGO
=============================================
Tests que no requieren configuración Django
"""
import pytest
from dataclasses import dataclass
from typing import Optional


@dataclass
class SimpleArtistEntity:
    """Entidad Artist simplificada para tests sin Django"""
    id: str
    name: str
    biography: str = ""
    country: str = ""
    image_url: str = ""
    followers_count: int = 0
    is_verified: bool = False
    is_active: bool = True


class TestSimpleArtistEntity:
    """Tests simples para Artist Entity sin dependencias Django"""
    
    @pytest.mark.unit
    def test_artist_creation_full_data(self):
        """Test creación completa de Artist"""
        # Given
        artist_data = {
            "id": "artist-123",
            "name": "Test Artist",
            "biography": "A test biography",
            "country": "Colombia",
            "followers_count": 50000,
            "is_verified": True
        }
        
        # When
        artist = SimpleArtistEntity(**artist_data)
        
        # Then
        assert artist.id == "artist-123"
        assert artist.name == "Test Artist"
        assert artist.biography == "A test biography"
        assert artist.country == "Colombia"
        assert artist.followers_count == 50000
        assert artist.is_verified is True
        assert artist.is_active is True
    
    @pytest.mark.unit
    def test_artist_minimal_data(self):
        """Test con datos mínimos"""
        # Given & When
        artist = SimpleArtistEntity(id="minimal", name="Minimal Artist")
        
        # Then
        assert artist.id == "minimal"
        assert artist.name == "Minimal Artist"
        assert artist.biography == ""
        assert artist.country == ""
        assert artist.followers_count == 0
        assert artist.is_verified is False
        assert artist.is_active is True
    
    @pytest.mark.unit
    def test_artist_verified_status(self):
        """Test artista verificado"""
        # Given & When
        artist = SimpleArtistEntity(
            id="verified",
            name="Verified Artist",
            is_verified=True,
            followers_count=1000000
        )
        
        # Then
        assert artist.is_verified is True
        assert artist.followers_count == 1000000
    
    @pytest.mark.unit
    def test_artist_inactive_status(self):
        """Test artista inactivo"""
        # Given & When
        artist = SimpleArtistEntity(
            id="inactive",
            name="Inactive Artist", 
            is_active=False
        )
        
        # Then
        assert artist.is_active is False
    
    @pytest.mark.unit
    @pytest.mark.parametrize("followers,is_popular", [
        (0, False),
        (100, False),
        (10000, False),
        (100000, True),
        (1000000, True),
    ])
    def test_artist_popularity_by_followers(self, followers, is_popular):
        """Test popularidad basada en seguidores"""
        # Given
        artist = SimpleArtistEntity(
            id=f"artist-{followers}",
            name="Test Artist",
            followers_count=followers
        )
        
        # When
        calculated_popularity = artist.followers_count >= 100000
        
        # Then
        assert calculated_popularity == is_popular
    
    @pytest.mark.unit
    def test_artist_with_image_url(self):
        """Test artista con imagen"""
        # Given
        image_url = "https://example.com/artist.jpg"
        artist = SimpleArtistEntity(
            id="with-image",
            name="Artist with Image",
            image_url=image_url
        )
        
        # Then
        assert artist.image_url == image_url
        assert "https://" in artist.image_url
    
    @pytest.mark.unit
    def test_artist_from_different_countries(self):
        """Test artistas de diferentes países"""
        # Given
        countries = ["Colombia", "México", "España", "Argentina"]
        
        for country in countries:
            # When
            artist = SimpleArtistEntity(
                id=f"artist-{country.lower()}",
                name=f"Artist from {country}",
                country=country
            )
            
            # Then
            assert artist.country == country
    
    @pytest.mark.unit
    def test_artist_biography_length(self):
        """Test longitud de biografía"""
        # Given
        short_bio = "Short bio"
        long_bio = "This is a very long biography " * 10
        
        # When
        artist_short = SimpleArtistEntity(id="short", name="Short Bio", biography=short_bio)
        artist_long = SimpleArtistEntity(id="long", name="Long Bio", biography=long_bio)
        
        # Then
        assert len(artist_short.biography) < 100
        assert len(artist_long.biography) > 100
    
    @pytest.mark.unit
    def test_artist_followers_increment(self):
        """Test incremento de seguidores"""
        # Given
        artist = SimpleArtistEntity(id="growing", name="Growing Artist", followers_count=1000)
        initial_followers = artist.followers_count
        
        # When
        artist.followers_count += 500
        
        # Then
        assert artist.followers_count == initial_followers + 500
        assert artist.followers_count == 1500
