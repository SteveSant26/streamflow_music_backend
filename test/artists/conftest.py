"""
Configuración compartida para los tests de artists
"""

from datetime import datetime

import pytest

from apps.artists.domain.entities import ArtistEntity


@pytest.fixture
def valid_artist_data():
    """Datos válidos para crear un artista"""
    return {
        "name": "Test Artist",
        "biography": "Una biografía de prueba para el artista de test",
        "country": "Test Country",
        "image_url": "https://example.com/artist-image.jpg",
        "followers_count": 50000,
        "is_verified": True,
        "is_active": True,
    }


@pytest.fixture
def artist_entity():
    """Entidad de artista para tests"""
    return ArtistEntity(
        id="test-artist-123",
        name="Test Artist Entity",
        biography="Biografía de test para entidad",
        country="Test Country",
        image_url="https://example.com/entity-image.jpg",
        followers_count=75000,
        is_verified=True,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def minimal_artist_data():
    """Datos mínimos para crear un artista"""
    return {"name": "Minimal Artist"}


@pytest.fixture
def artists_list():
    """Lista de artistas para tests"""
    return [
        ArtistEntity(
            id=f"artist-{i}",
            name=f"Artist {i}",
            biography=f"Biografía del artista {i}",
            country="Test Country" if i % 2 == 0 else "Other Country",
            followers_count=1000 * i,
            is_verified=i % 3 == 0,
            is_active=True,
        )
        for i in range(1, 6)
    ]


@pytest.fixture
def popular_artists():
    """Lista de artistas populares ordenados por seguidores"""
    return [
        ArtistEntity(
            id=f"popular-{i}",
            name=f"Popular Artist {i}",
            followers_count=100000 - (i * 10000),
            is_verified=True,
            is_active=True,
        )
        for i in range(1, 4)
    ]


@pytest.fixture
def verified_artists():
    """Lista de artistas verificados"""
    return [
        ArtistEntity(
            id=f"verified-{i}",
            name=f"Verified Artist {i}",
            followers_count=50000 + (i * 5000),
            is_verified=True,
            is_active=True,
        )
        for i in range(1, 4)
    ]
