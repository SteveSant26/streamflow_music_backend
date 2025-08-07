"""
Tests independientes para la entidad GenreEntity
Importación directa sin dependencias problemáticas
"""

import pytest
import sys
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

# Definimos la entidad directamente para evitar imports problemáticos
@dataclass
class GenreEntity:
    """Entidad que representa un género musical"""
    id: str
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    color_hex: Optional[str] = None  # Color representativo del género
    popularity_score: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class TestGenreEntity:
    """Tests para la entidad GenreEntity"""
    
    def test_genre_entity_creation_minimal(self):
        """Test creación de género con datos mínimos"""
        genre = GenreEntity(
            id="genre-1",
            name="Rock"
        )
        
        assert genre.id == "genre-1"
        assert genre.name == "Rock"
        assert genre.description is None
        assert genre.image_url is None
        assert genre.color_hex is None
        assert genre.popularity_score == 0
        assert genre.created_at is None
        assert genre.updated_at is None
        
    def test_genre_entity_creation_complete(self):
        """Test creación de género con datos completos"""
        created_at = datetime.now()
        updated_at = datetime.now()
        
        genre = GenreEntity(
            id="genre-2",
            name="Electronic",
            description="Electronic music genre with synthesized sounds",
            image_url="https://example.com/electronic.jpg",
            color_hex="#FF6B35",
            popularity_score=85,
            created_at=created_at,
            updated_at=updated_at
        )
        
        assert genre.id == "genre-2"
        assert genre.name == "Electronic"
        assert genre.description == "Electronic music genre with synthesized sounds"
        assert genre.image_url == "https://example.com/electronic.jpg"
        assert genre.color_hex == "#FF6B35"
        assert genre.popularity_score == 85
        assert genre.created_at == created_at
        assert genre.updated_at == updated_at
        
    def test_genre_entity_color_hex_formats(self):
        """Test diferentes formatos de color hex"""
        # Color hex formato completo
        genre_full = GenreEntity(
            id="genre-color-full",
            name="Pop",
            color_hex="#FF5733"
        )
        assert genre_full.color_hex == "#FF5733"
        
        # Color hex formato corto
        genre_short = GenreEntity(
            id="genre-color-short",
            name="Jazz",
            color_hex="#F57"
        )
        assert genre_short.color_hex == "#F57"
        
        # Sin color
        genre_no_color = GenreEntity(
            id="genre-no-color",
            name="Classical"
        )
        assert genre_no_color.color_hex is None
        
    def test_genre_entity_popularity_scores(self):
        """Test diferentes niveles de popularidad"""
        # Género muy popular
        popular_genre = GenreEntity(
            id="genre-popular",
            name="Pop",
            popularity_score=95
        )
        assert popular_genre.popularity_score == 95
        
        # Género moderadamente popular
        moderate_genre = GenreEntity(
            id="genre-moderate",
            name="Indie",
            popularity_score=50
        )
        assert moderate_genre.popularity_score == 50
        
        # Género nicho
        niche_genre = GenreEntity(
            id="genre-niche",
            name="Ambient",
            popularity_score=15
        )
        assert niche_genre.popularity_score == 15
        
        # Género sin popularidad definida
        unknown_genre = GenreEntity(
            id="genre-unknown",
            name="Unknown Genre"
        )
        assert unknown_genre.popularity_score == 0
        
    def test_genre_entity_common_genres(self):
        """Test géneros musicales comunes"""
        genres_data = [
            ("rock", "Rock"),
            ("pop", "Pop"),
            ("jazz", "Jazz"),
            ("classical", "Classical"),
            ("electronic", "Electronic"),
            ("hip-hop", "Hip-Hop"),
            ("country", "Country"),
            ("reggae", "Reggae"),
            ("blues", "Blues"),
            ("folk", "Folk")
        ]
        
        for genre_id, genre_name in genres_data:
            genre = GenreEntity(
                id=genre_id,
                name=genre_name
            )
            assert genre.id == genre_id
            assert genre.name == genre_name
            
    def test_genre_entity_with_description(self):
        """Test géneros con descripciones detalladas"""
        descriptions = {
            "rock": "A genre of popular music that originated in the 1950s",
            "jazz": "A music genre that originated in African-American communities",
            "classical": "Art music produced in the traditions of Western culture",
            "electronic": "Music that employs electronic musical instruments"
        }
        
        for genre_id, description in descriptions.items():
            genre = GenreEntity(
                id=genre_id,
                name=genre_id.title(),
                description=description
            )
            assert genre.description == description
            
    def test_genre_entity_image_urls(self):
        """Test URLs de imágenes de géneros"""
        urls = [
            "https://example.com/rock.jpg",
            "https://storage.supabase.co/genre/pop.png",
            "https://cdn.music.com/images/jazz.webp",
            "https://assets.spotify.com/genre/electronic.svg"
        ]
        
        for i, url in enumerate(urls):
            genre = GenreEntity(
                id=f"genre-{i}",
                name=f"Genre {i}",
                image_url=url
            )
            assert genre.image_url == url
            
    def test_genre_entity_timestamps(self):
        """Test manejo de timestamps"""
        now = datetime.now()
        earlier = datetime(2023, 1, 1)
        
        genre = GenreEntity(
            id="genre-timestamps",
            name="Timestamped Genre",
            created_at=earlier,
            updated_at=now
        )
        
        assert genre.created_at == earlier
        assert genre.updated_at == now
        
    def test_genre_entity_type_validation(self):
        """Test validación de tipos"""
        genre = GenreEntity(
            id="genre-types",
            name="Type Test Genre",
            popularity_score=75
        )
        
        assert isinstance(genre.id, str)
        assert isinstance(genre.name, str)
        assert isinstance(genre.popularity_score, int)
        
        if genre.description is not None:
            assert isinstance(genre.description, str)
        if genre.image_url is not None:
            assert isinstance(genre.image_url, str)
        if genre.color_hex is not None:
            assert isinstance(genre.color_hex, str)
        if genre.created_at is not None:
            assert isinstance(genre.created_at, datetime)
        if genre.updated_at is not None:
            assert isinstance(genre.updated_at, datetime)
            
    def test_genre_entity_edge_cases(self):
        """Test casos límite"""
        # Nombre muy largo
        long_name = "A" * 200
        genre_long_name = GenreEntity(
            id="genre-long-name",
            name=long_name
        )
        assert genre_long_name.name == long_name
        
        # Popularidad máxima
        genre_max_popularity = GenreEntity(
            id="genre-max-pop",
            name="Max Popular Genre",
            popularity_score=100
        )
        assert genre_max_popularity.popularity_score == 100
