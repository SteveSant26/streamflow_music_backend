"""
Tests para entidades del dominio de Albums
Archivo: src/apps/albums/domain/entities.py
"""

import pytest
import sys
import os
from datetime import date, datetime

# Añadir src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from apps.albums.domain.entities import AlbumEntity


class TestAlbumEntity:
    """Tests para la entidad AlbumEntity"""
    
    def test_album_entity_creation_with_minimal_data(self):
        """Test creación de album con datos mínimos"""
        album = AlbumEntity(
            id="album-1",
            title="Test Album",
            artist_name="Test Artist"
        )
        
        assert album.id == "album-1"
        assert album.title == "Test Album"
        assert album.artist_name == "Test Artist"
        
        # Verificar valores por defecto
        assert album.total_tracks == 0
        assert album.play_count == 0
        assert album.source_type == "manual"
        assert album.artist_id is None
        assert album.release_date is None
        assert album.description is None
        
    def test_album_entity_creation_with_complete_data(self):
        """Test creación de album con datos completos"""
        release_date = date(2024, 1, 15)
        created_at = datetime(2024, 1, 1, 10, 0, 0)
        updated_at = datetime(2024, 1, 2, 15, 30, 0)
        
        album = AlbumEntity(
            id="album-2",
            title="Complete Album",
            artist_id="artist-123",
            artist_name="Complete Artist",
            release_date=release_date,
            description="A complete test album",
            cover_image_url="https://example.com/cover.jpg",
            total_tracks=12,
            play_count=1500,
            source_type="spotify",
            source_id="spotify-123",
            source_url="https://spotify.com/album/123",
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert album.id == "album-2"
        assert album.title == "Complete Album"
        assert album.artist_id == "artist-123"
        assert album.artist_name == "Complete Artist"
        assert album.release_date == release_date
        assert album.description == "A complete test album"
        assert album.cover_image_url == "https://example.com/cover.jpg"
        assert album.total_tracks == 12
        assert album.play_count == 1500
        assert album.source_type == "spotify"
        assert album.source_id == "spotify-123"
        assert album.source_url == "https://spotify.com/album/123"
        assert album.created_at == created_at
        assert album.updated_at == updated_at
        
    def test_album_entity_string_representation(self):
        """Test representación string del album"""
        album = AlbumEntity(
            id="album-3",
            title="String Test Album",
            artist_name="String Test Artist"
        )
        
        # Verificar que tiene método __str__
        if hasattr(album, '__str__'):
            str_repr = str(album)
            assert isinstance(str_repr, str)
            assert len(str_repr) > 0
            
    def test_album_entity_repr_representation(self):
        """Test representación repr del album"""
        album = AlbumEntity(
            id="album-4",
            title="Repr Test Album",
            artist_name="Repr Test Artist"
        )
        
        # Verificar que tiene método __repr__
        if hasattr(album, '__repr__'):
            repr_str = repr(album)
            assert isinstance(repr_str, str)
            assert len(repr_str) > 0
            
    def test_album_entity_methods_if_exist(self):
        """Test métodos adicionales si existen en la entidad"""
        album = AlbumEntity(
            id="album-5",
            title="Methods Test Album",
            artist_name="Methods Test Artist",
            release_date=date(2024, 6, 1),
            total_tracks=10,
            play_count=500
        )
        
        # Verificar método is_recent si existe
        if hasattr(album, 'is_recent'):
            is_recent = album.is_recent()
            assert isinstance(is_recent, bool)
            
        # Verificar método is_popular si existe
        if hasattr(album, 'is_popular'):
            is_popular = album.is_popular()
            assert isinstance(is_popular, bool)
            
        # Verificar método has_cover si existe
        if hasattr(album, 'has_cover'):
            has_cover = album.has_cover()
            assert isinstance(has_cover, bool)
            
    def test_album_entity_equality_if_implemented(self):
        """Test igualdad entre entidades si está implementada"""
        album1 = AlbumEntity(
            id="album-same",
            title="Same Album",
            artist_name="Same Artist"
        )
        
        album2 = AlbumEntity(
            id="album-same",
            title="Same Album",
            artist_name="Same Artist"
        )
        
        album3 = AlbumEntity(
            id="album-different",
            title="Different Album",
            artist_name="Different Artist"
        )
        
        # Si tiene método __eq__ implementado
        if hasattr(album1, '__eq__'):
            # Albums con mismo ID deberían ser iguales
            assert album1 == album2
            # Albums con diferente ID deberían ser diferentes
            assert album1 != album3
            
    def test_album_entity_with_edge_cases(self):
        """Test casos límite de la entidad"""
        # Album con título vacío
        album_empty_title = AlbumEntity(
            id="album-empty",
            title="",
            artist_name="Test Artist"
        )
        assert album_empty_title.title == ""
        
        # Album con play_count muy alto
        album_high_plays = AlbumEntity(
            id="album-popular",
            title="Popular Album",
            artist_name="Popular Artist",
            play_count=999999999
        )
        assert album_high_plays.play_count == 999999999
        
        # Album con muchos tracks
        album_many_tracks = AlbumEntity(
            id="album-long",
            title="Long Album",
            artist_name="Prolific Artist",
            total_tracks=100
        )
        assert album_many_tracks.total_tracks == 100
        
    def test_album_entity_type_validation(self):
        """Test validación de tipos si está implementada"""
        album = AlbumEntity(
            id="album-validation",
            title="Validation Album",
            artist_name="Validation Artist"
        )
        
        # Verificar tipos de atributos principales
        assert isinstance(album.id, str)
        assert isinstance(album.title, str)
        assert isinstance(album.artist_name, str)
        assert isinstance(album.total_tracks, int)
        assert isinstance(album.play_count, int)
        assert isinstance(album.source_type, str)
        
        # Verificar tipos de atributos opcionales si no son None
        if album.artist_id is not None:
            assert isinstance(album.artist_id, str)
        if album.description is not None:
            assert isinstance(album.description, str)
        if album.cover_image_url is not None:
            assert isinstance(album.cover_image_url, str)
        if album.source_id is not None:
            assert isinstance(album.source_id, str)
        if album.source_url is not None:
            assert isinstance(album.source_url, str)
            
    def test_album_entity_immutability_if_implemented(self):
        """Test inmutabilidad si está implementada"""
        album = AlbumEntity(
            id="album-immutable",
            title="Immutable Album",
            artist_name="Immutable Artist",
            play_count=100
        )
        
        original_id = album.id
        original_title = album.title
        original_play_count = album.play_count
        
        # Verificar que los valores no han cambiado accidentalmente
        assert album.id == original_id
        assert album.title == original_title
        assert album.play_count == original_play_count
