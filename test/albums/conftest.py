"""
Configuración de pytest para tests de Albums
"""

import os
import sys
from datetime import date, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

# Agregar el proyecto al path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..")
sys.path.insert(0, project_root)

# Importaciones necesarias
try:
    from src.apps.albums.domain.entities import AlbumEntity
except ImportError:
    pytest.skip("No se pueden importar entidades de Albums", allow_module_level=True)


@pytest.fixture
def sample_album_entity():
    """Fixture para crear una entidad de álbum de prueba"""
    return AlbumEntity(
        id=str(uuid4()),
        title="Test Album",
        artist_id=str(uuid4()),
        artist_name="Test Artist",
        release_date=date(2020, 1, 1),
        description="Test album description",
        cover_image_url="https://example.com/cover.jpg",
        total_tracks=10,
        play_count=1000,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def minimal_album_entity():
    """Fixture para álbum con datos mínimos"""
    return AlbumEntity(
        id=str(uuid4()),
        title="Minimal Album",
        artist_id=str(uuid4()),
        artist_name="Minimal Artist",
    )


@pytest.fixture
def mock_album_repository():
    """Fixture para repositorio mock"""
    repo = Mock()

    # Configurar métodos comunes
    repo.get_by_id.return_value = None
    repo.get_all.return_value = []
    repo.find_by_artist_id.return_value = []
    repo.search_by_title.return_value = []
    repo.get_recent_albums.return_value = []
    repo.get_popular_albums.return_value = []
    repo.find_by_release_year.return_value = []

    return repo


@pytest.fixture
def sample_albums_list(sample_album_entity):
    """Fixture para lista de álbumes de prueba"""
    albums = []
    for i in range(3):
        album = AlbumEntity(
            id=str(uuid4()),
            title=f"Album {i+1}",
            artist_id=str(uuid4()),
            artist_name=f"Artist {i+1}",
            release_date=date(2020 + i, 1, 1),
            total_tracks=10 + i,
            play_count=1000 * (i + 1),
            is_active=True,
        )
        albums.append(album)
    return albums


def create_mock_album(
    album_id: str = None,
    title: str = "Mock Album",
    artist_name: str = "Mock Artist",
    **kwargs,
) -> AlbumEntity:
    """Función helper para crear álbumes mock"""
    defaults = {
        "id": album_id or str(uuid4()),
        "title": title,
        "artist_id": str(uuid4()),
        "artist_name": artist_name,
        "release_date": date(2020, 1, 1),
        "total_tracks": 10,
        "play_count": 1000,
        "is_active": True,
    }
    defaults.update(kwargs)
    return AlbumEntity(**defaults)


# Configuración de pytest
def pytest_configure(config):
    """Configuración global de pytest"""
    config.addinivalue_line("markers", "unit: marca tests unitarios")
    config.addinivalue_line("markers", "integration: marca tests de integración")
    config.addinivalue_line("markers", "slow: marca tests lentos")


def pytest_collection_modifyitems(config, items):
    """Modificar la colección de tests"""
    for item in items:
        # Agregar marcador 'unit' por defecto
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)
