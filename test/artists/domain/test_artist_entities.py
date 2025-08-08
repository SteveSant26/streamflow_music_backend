"""
Tests para entidades del dominio de Artists
Archivo: src/apps/artists/domain/entities.py
"""

import pytest
import sys
import os

# Añadir src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from apps.artists.domain.entities import ArtistEntity


class TestArtistEntity:
    """Tests para la entidad ArtistEntity"""
    
    def test_artist_entity_creation_minimal(self):
        """Test creación de artista con datos mínimos"""
        artist = ArtistEntity(
            id="artist-1",
            name="Test Artist"
        )
        
        assert artist.id == "artist-1"
        assert artist.name == "Test Artist"
        assert artist.followers_count == 0
        assert artist.is_verified is False
        assert artist.is_active is True
        
    def test_artist_entity_creation_complete(self):
        """Test creación de artista con datos completos"""
        artist = ArtistEntity(
            id="artist-2",
            name="Complete Artist",
            biography="A complete artist biography",
            image_url="https://example.com/artist.jpg",
            followers_count=50000,
            is_verified=True,
            is_active=True
        )
        
        assert artist.id == "artist-2"
        assert artist.name == "Complete Artist"
        assert artist.biography == "A complete artist biography"
        assert artist.image_url == "https://example.com/artist.jpg"
        assert artist.followers_count == 50000
        assert artist.is_verified is True
        assert artist.is_active is True
        
    def test_artist_entity_popularity_method_if_exists(self):
        """Test método de popularidad si existe"""
        # Artista con muchos seguidores
        popular_artist = ArtistEntity(
            id="artist-popular",
            name="Popular Artist",
            followers_count=1000000
        )
        
        # Artista con pocos seguidores
        unknown_artist = ArtistEntity(
            id="artist-unknown",
            name="Unknown Artist",
            followers_count=100
        )
        
        # Si tiene método is_popular
        if hasattr(popular_artist, 'is_popular'):
            popular_result = popular_artist.is_popular()
            unknown_result = unknown_artist.is_popular()
            
            assert isinstance(popular_result, bool)
            assert isinstance(unknown_result, bool)
            
    def test_artist_entity_string_representation(self):
        """Test representación string del artista"""
        artist = ArtistEntity(
            id="artist-str",
            name="String Test Artist"
        )
        
        if hasattr(artist, '__str__'):
            str_repr = str(artist)
            assert isinstance(str_repr, str)
            assert len(str_repr) > 0
            
    def test_artist_entity_verification_status(self):
        """Test estado de verificación"""
        verified_artist = ArtistEntity(
            id="artist-verified",
            name="Verified Artist",
            is_verified=True
        )
        
        unverified_artist = ArtistEntity(
            id="artist-unverified",
            name="Unverified Artist",
            is_verified=False
        )
        
        assert verified_artist.is_verified is True
        assert unverified_artist.is_verified is False
        
    def test_artist_entity_activity_status(self):
        """Test estado de actividad"""
        active_artist = ArtistEntity(
            id="artist-active",
            name="Active Artist",
            is_active=True
        )
        
        inactive_artist = ArtistEntity(
            id="artist-inactive",
            name="Inactive Artist",
            is_active=False
        )
        
        assert active_artist.is_active is True
        assert inactive_artist.is_active is False
        
    def test_artist_entity_edge_cases(self):
        """Test casos límite"""
        # Artista con nombre vacío
        empty_name_artist = ArtistEntity(
            id="artist-empty",
            name=""
        )
        assert empty_name_artist.name == ""
        
        # Artista con muchos seguidores
        mega_artist = ArtistEntity(
            id="artist-mega",
            name="Mega Artist",
            followers_count=999999999
        )
        assert mega_artist.followers_count == 999999999
        
    def test_artist_entity_type_validation(self):
        """Test validación de tipos"""
        artist = ArtistEntity(
            id="artist-types",
            name="Type Test Artist"
        )
        
        assert isinstance(artist.id, str)
        assert isinstance(artist.name, str)
        assert isinstance(artist.followers_count, int)
        assert isinstance(artist.is_verified, bool)
        assert isinstance(artist.is_active, bool)
        
        if artist.biography is not None:
            assert isinstance(artist.biography, str)
        if artist.image_url is not None:
            assert isinstance(artist.image_url, str)
            
    def test_artist_entity_with_none_values(self):
        """Test manejo de valores None"""
        artist = ArtistEntity(
            id="artist-none",
            name="None Test Artist",
            biography=None,
            image_url=None
        )
        
        assert artist.biography is None
        assert artist.image_url is None
        
    def test_artist_entity_equality_if_implemented(self):
        """Test igualdad entre entidades si está implementada"""
        artist1 = ArtistEntity(
            id="artist-same",
            name="Same Artist"
        )
        
        artist2 = ArtistEntity(
            id="artist-same",
            name="Same Artist"
        )
        
        artist3 = ArtistEntity(
            id="artist-different",
            name="Different Artist"
        )
        
        if hasattr(artist1, '__eq__'):
            assert artist1 == artist2
            assert artist1 != artist3
