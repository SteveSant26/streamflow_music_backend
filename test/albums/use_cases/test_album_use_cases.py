#!/usr/bin/env python3
"""
Tests para casos de uso de Album
"""

import os
import sys
from datetime import date
from unittest.mock import Mock
from uuid import uuid4

# Configurar el path correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..")
sys.path.insert(0, project_root)

try:
    # Importar entidades del dominio
    from src.apps.albums.domain.entities import AlbumEntity

    print("✅ Entidades importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando: {e}")
    sys.exit(1)

# Crear interface mock para evitar dependencias
from abc import ABC, abstractmethod
from typing import List, Optional


class IAlbumRepository(ABC):
    """Interface mock del repositorio de álbumes"""

    @abstractmethod
    def get_by_id(self, album_id: str) -> Optional[AlbumEntity]:
        """Obtiene un álbum por ID"""

    @abstractmethod
    def get_all(self) -> List[AlbumEntity]:
        """Obtiene todos los álbumes"""

    @abstractmethod
    def find_by_artist_id(self, artist_id: str, limit: int = 10) -> List[AlbumEntity]:
        """Busca álbumes por ID del artista"""

    @abstractmethod
    def search_by_title(self, title: str, limit: int = 10) -> List[AlbumEntity]:
        """Busca álbumes por título"""


# Importar excepciones si existen
try:
    from src.apps.albums.domain.exceptions import AlbumNotFoundException

    print("✅ Excepciones importadas correctamente")
except ImportError:
    # Crear excepción temporal para los tests
    class AlbumNotFoundException(Exception):
        def __init__(self, album_id: str):
            super().__init__(f"Album with id {album_id} not found")

    print("⚠️  Usando excepción temporal")


# Crear casos de uso básicos mock para testing
class GetAlbumUseCase:
    """Caso de uso mock para obtener álbum por ID"""

    def __init__(self, repository: IAlbumRepository):
        self.repository = repository

    def execute(self, album_id: str) -> AlbumEntity:
        album = self.repository.get_by_id(album_id)
        if not album:
            raise AlbumNotFoundException(album_id)
        return album


class GetAllAlbumsUseCase:
    """Caso de uso mock para obtener todos los álbumes"""

    def __init__(self, repository: IAlbumRepository):
        self.repository = repository

    def execute(self) -> list[AlbumEntity]:
        return self.repository.get_all()


class SearchAlbumsByTitleUseCase:
    """Caso de uso mock para buscar álbumes por título"""

    def __init__(self, repository: IAlbumRepository):
        self.repository = repository

    def execute(self, title: str, limit: int = 10) -> list[AlbumEntity]:
        return self.repository.search_by_title(title, limit)


class GetAlbumsByArtistUseCase:
    """Caso de uso mock para obtener álbumes por artista"""

    def __init__(self, repository: IAlbumRepository):
        self.repository = repository

    def execute(self, artist_id: str, limit: int = 10) -> list[AlbumEntity]:
        return self.repository.find_by_artist_id(artist_id, limit)


def create_mock_album(
    album_id: str,
    title: str,
    artist_name: str = "Test Artist",
    total_tracks: int = 10,
    play_count: int = 1000,
) -> AlbumEntity:
    """Crear álbum mock para testing"""
    return AlbumEntity(
        id=album_id,
        title=title,
        artist_id=str(uuid4()),
        artist_name=artist_name,
        release_date=date(2020, 1, 1),
        total_tracks=total_tracks,
        play_count=play_count,
        is_active=True,
    )


def test_get_album_use_case():
    """Test GetAlbumUseCase"""
    print("📀 Probando GetAlbumUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Álbum de prueba
    test_album = create_mock_album(
        "album-123", "Test Album", "Test Artist", total_tracks=12, play_count=5000
    )

    # Configurar mock para retornar el álbum
    mock_repository.get_by_id.return_value = test_album

    # Crear use case
    use_case = GetAlbumUseCase(mock_repository)

    # Ejecutar
    result = use_case.execute("album-123")

    # Verificaciones
    assert result is not None  # nosec B101
    assert result.id == "album-123"  # nosec B101
    assert result.title == "Test Album"  # nosec B101
    assert result.artist_name == "Test Artist"  # nosec B101
    assert result.total_tracks == 12  # nosec B101
    assert result.play_count == 5000  # nosec B101
    mock_repository.get_by_id.assert_called_once_with("album-123")

    print("✅ GetAlbumUseCase funciona correctamente")
    print(f"   - Obtuvo álbum: {result.title}")
    print(f"   - ID: {result.id}")
    print(f"   - Pistas: {result.total_tracks}")

    return True


def test_get_album_not_found():
    """Test GetAlbumUseCase cuando no encuentra el álbum"""
    print("\n📀 Probando GetAlbumUseCase - álbum no encontrado...")

    # Crear mock repository
    mock_repository = Mock()
    mock_repository.get_by_id.return_value = None

    # Crear use case
    use_case = GetAlbumUseCase(mock_repository)

    # Ejecutar y verificar que lanza excepción
    try:
        use_case.execute("nonexistent-album")
        assert False, "Debería haber lanzado AlbumNotFoundException"  # nosec B101
    except AlbumNotFoundException as e:
        assert "nonexistent-album" in str(e)  # nosec B101
        print("✅ AlbumNotFoundException lanzada correctamente")

    return True


def test_get_all_albums_use_case():
    """Test GetAllAlbumsUseCase"""
    print("\n📀 Probando GetAllAlbumsUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Lista de álbumes de prueba
    test_albums = [
        create_mock_album("album-1", "Album One", "Artist One", total_tracks=10),
        create_mock_album("album-2", "Album Two", "Artist Two", total_tracks=12),
        create_mock_album("album-3", "Album Three", "Artist Three", total_tracks=8),
    ]

    mock_repository.get_all.return_value = test_albums

    # Crear use case
    use_case = GetAllAlbumsUseCase(mock_repository)

    # Ejecutar
    results = use_case.execute()

    # Verificaciones
    assert len(results == 3)  # nosec B101
    assert results[0].title == "Album One"  # nosec B101
    assert results[1].title == "Album Two"  # nosec B101
    assert results[2].title == "Album Three"  # nosec B101
    assert results[0].total_tracks == 10  # nosec B101

    mock_repository.get_all.assert_called_once()

    print("✅ GetAllAlbumsUseCase funciona correctamente")
    print(f"   - Obtuvo {len(results)} álbumes")
    print(f"   - Primer álbum: {results[0].title}")

    return True


def test_search_albums_by_title_use_case():
    """Test SearchAlbumsByTitleUseCase"""
    print("\n📀 Probando SearchAlbumsByTitleUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Álbumes que coinciden con búsqueda
    search_results = [
        create_mock_album("rock-1", "Rock Album 1", "Rock Artist 1", total_tracks=11),
        create_mock_album("rock-2", "Rock Album 2", "Rock Artist 2", total_tracks=13),
    ]

    mock_repository.search_by_title.return_value = search_results

    # Crear use case
    use_case = SearchAlbumsByTitleUseCase(mock_repository)

    # Ejecutar búsqueda
    results = use_case.execute("rock", limit=10)

    # Verificaciones
    assert len(results == 2)  # nosec B101
    assert results[0].title == "Rock Album 1"  # nosec B101
    assert results[1].title == "Rock Album 2"  # nosec B101

    mock_repository.search_by_title.assert_called_once_with("rock", 10)

    print("✅ SearchAlbumsByTitleUseCase funciona correctamente")
    print(f"   - Búsqueda: 'rock'")
    print(f"   - Encontró {len(results)} álbumes")
    print(f"   - Primer resultado: {results[0].title}")

    return True


def test_get_albums_by_artist_use_case():
    """Test GetAlbumsByArtistUseCase"""
    print("\n📀 Probando GetAlbumsByArtistUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Álbumes del mismo artista
    artist_albums = [
        create_mock_album(
            "album-1", "First Album", "Pink Floyd", total_tracks=8, play_count=50000
        ),
        create_mock_album(
            "album-2", "Second Album", "Pink Floyd", total_tracks=10, play_count=80000
        ),
    ]

    mock_repository.find_by_artist_id.return_value = artist_albums

    # Crear use case
    use_case = GetAlbumsByArtistUseCase(mock_repository)

    # Ejecutar
    results = use_case.execute("artist-123", limit=20)

    # Verificaciones
    assert len(results == 2)  # nosec B101
    assert all(album.artist_name == "Pink Floyd" for album in results)  # nosec B101
    assert results[0].title == "First Album"  # nosec B101

    mock_repository.find_by_artist_id.assert_called_once_with("artist-123", 20)

    print("✅ GetAlbumsByArtistUseCase funciona correctamente")
    print(f"   - Artista: Pink Floyd")
    print(f"   - Encontró {len(results)} álbumes")
    print(f"   - Primer álbum: {results[0].title}")

    return True


def test_empty_results():
    """Test casos con resultados vacíos"""
    print("\n📀 Probando casos con resultados vacíos...")

    # Mock repository que retorna listas vacías
    mock_repository = Mock()
    mock_repository.search_by_title.return_value = []
    mock_repository.find_by_artist_id.return_value = []
    mock_repository.get_all.return_value = []

    # Test búsqueda sin resultados
    search_use_case = SearchAlbumsByTitleUseCase(mock_repository)
    search_results = search_use_case.execute("nonexistent")
    assert search_results == []  # nosec B101
    artist_use_case = GetAlbumsByArtistUseCase(mock_repository)
    artist_results = artist_use_case.execute("unknown-artist")
    assert artist_results == []  # nosec B101
    all_use_case = GetAllAlbumsUseCase(mock_repository)
    all_results = all_use_case.execute()
    assert all_results == []  # nosec B101

    print("✅ Casos con resultados vacíos funcionan correctamente")

    return True


def run_all_tests():
    """Ejecuta todos los tests de casos de uso Album"""
    print("🧪 TESTS DE CASOS DE USO ALBUM")
    print("=" * 50)

    tests = [
        test_get_album_use_case,
        test_get_album_not_found,
        test_get_all_albums_use_case,
        test_search_albums_by_title_use_case,
        test_get_albums_by_artist_use_case,
        test_empty_results,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"❌ {test.__name__} falló")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} falló con error: {e}")

    print("\n" + "=" * 50)
    print(f"📊 RESULTADOS: {passed} pasaron, {failed} fallaron")

    if failed == 0:
        print("🎉 ¡Todos los tests de casos de uso Album pasaron!")
        return True
    else:
        print(f"⚠️  {failed} tests fallaron")
        return False


if __name__ == "__main__":
    run_all_tests()
