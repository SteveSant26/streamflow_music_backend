#!/usr/bin/env python
"""
Test directo para verificar que los casos de uso de Artists funcionan
"""
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

# Configurar paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

# Configurar Django con env de desarrollo
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env.dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django

django.setup()

# Importar después de setup
from apps.artists.domain.entities import ArtistEntity
from apps.artists.domain.exceptions import ArtistNotFoundException
from apps.artists.use_cases import (
    GetAllArtistsUseCase,
    GetArtistsByCountryUseCase,
    GetArtistUseCase,
    GetPopularArtistsUseCase,
    GetVerifiedArtistsUseCase,
    SearchArtistsByNameUseCase,
)


def create_mock_artist(artist_id: str, name: str, **kwargs) -> ArtistEntity:
    """Helper para crear artistas mock"""
    return ArtistEntity(
        id=artist_id,
        name=name,
        biography=kwargs.get("biography", f"Biografía de {name}"),
        country=kwargs.get("country", "Test Country"),
        image_url=kwargs.get("image_url", f"https://example.com/{artist_id}.jpg"),
        followers_count=kwargs.get("followers_count", 10000),
        is_verified=kwargs.get("is_verified", False),
        is_active=kwargs.get("is_active", True),
        created_at=kwargs.get("created_at", datetime.now()),
        updated_at=kwargs.get("updated_at", datetime.now()),
    )


def test_get_artist_use_case():
    """Test GetArtistUseCase"""
    print("🎤 Probando GetArtistUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Artista de prueba
    test_artist = create_mock_artist(
        "artist-123", "Test Artist", followers_count=50000, is_verified=True
    )

    # Configurar mock para retornar el artista
    mock_repository.get_by_id.return_value = test_artist

    # Crear use case
    use_case = GetArtistUseCase(mock_repository)

    # Ejecutar
    result = use_case.execute("artist-123")

    # Verificaciones
    assert result is not None  # nosec B101
    assert result.id == "artist-123"  # nosec B101
    assert result.name == "Test Artist"  # nosec B101
    assert result.followers_count == 50000  # nosec B101
    assert result.is_verified == True  # nosec B101
    mock_repository.get_by_id.assert_called_once_with("artist-123")

    print("✅ GetArtistUseCase funciona correctamente")
    print(f"   - Obtuvo artista: {result.name}")
    print(f"   - ID: {result.id}")
    print(f"   - Seguidores: {result.followers_count:,}")

    return True


def test_get_artist_not_found():
    """Test GetArtistUseCase cuando no encuentra el artista"""
    print("\n🎤 Probando GetArtistUseCase - artista no encontrado...")

    # Crear mock repository
    mock_repository = Mock()
    mock_repository.get_by_id.return_value = None

    # Crear use case
    use_case = GetArtistUseCase(mock_repository)

    # Ejecutar y verificar que lanza excepción
    try:
        use_case.execute("nonexistent-artist")
        assert False, "Debería haber lanzado ArtistNotFoundException"  # nosec B101
    except ArtistNotFoundException as e:
        # La excepción tiene un formato específico con diccionario
        assert "nonexistent-artist" in str(e)  # nosec B101
        assert "no encontrado" in str(e)  # nosec B101
        print("✅ ArtistNotFoundException lanzada correctamente")

    return True


def test_get_all_artists_use_case():
    """Test GetAllArtistsUseCase"""
    print("\n🎤 Probando GetAllArtistsUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Lista de artistas de prueba
    test_artists = [
        create_mock_artist("artist-1", "Artist One", followers_count=10000),
        create_mock_artist("artist-2", "Artist Two", followers_count=20000),
        create_mock_artist(
            "artist-3", "Artist Three", followers_count=30000, is_verified=True
        ),
    ]

    mock_repository.get_all.return_value = test_artists

    # Crear use case
    use_case = GetAllArtistsUseCase(mock_repository)

    # Ejecutar
    results = use_case.execute()

    # Verificaciones
    assert len(results == 3)  # nosec B101
    assert results[0].name == "Artist One"  # nosec B101
    assert results[1].name == "Artist Two"  # nosec B101
    assert results[2].name == "Artist Three"  # nosec B101
    assert results[2].is_verified == True  # nosec B101

    mock_repository.get_all.assert_called_once()

    print("✅ GetAllArtistsUseCase funciona correctamente")
    print(f"   - Obtuvo {len(results)} artistas")
    print(f"   - Primer artista: {results[0].name}")

    return True


def test_search_artists_by_name_use_case():
    """Test SearchArtistsByNameUseCase"""
    print("\n🎤 Probando SearchArtistsByNameUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Artistas que coinciden con búsqueda
    search_results = [
        create_mock_artist("rock-1", "Rock Artist 1", followers_count=15000),
        create_mock_artist("rock-2", "Rock Artist 2", followers_count=25000),
    ]

    mock_repository.search_by_name.return_value = search_results

    # Crear use case
    use_case = SearchArtistsByNameUseCase(mock_repository)

    # Ejecutar búsqueda
    results = use_case.execute("rock", limit=10)

    # Verificaciones
    assert len(results == 2)  # nosec B101
    assert results[0].name == "Rock Artist 1"  # nosec B101
    assert results[1].name == "Rock Artist 2"  # nosec B101

    mock_repository.search_by_name.assert_called_once_with("rock", 10)

    print("✅ SearchArtistsByNameUseCase funciona correctamente")
    print(f"   - Búsqueda: 'rock'")
    print(f"   - Encontró {len(results)} artistas")
    print(f"   - Primer resultado: {results[0].name}")

    return True


def test_get_artists_by_country_use_case():
    """Test GetArtistsByCountryUseCase"""
    print("\n🎤 Probando GetArtistsByCountryUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Artistas de Colombia
    colombian_artists = [
        create_mock_artist(
            "col-1", "Colombian Artist 1", country="Colombia", followers_count=40000
        ),
        create_mock_artist(
            "col-2",
            "Colombian Artist 2",
            country="Colombia",
            followers_count=60000,
            is_verified=True,
        ),
    ]

    mock_repository.find_by_country.return_value = colombian_artists

    # Crear use case
    use_case = GetArtistsByCountryUseCase(mock_repository)

    # Ejecutar
    results = use_case.execute("Colombia", limit=20)

    # Verificaciones
    assert len(results == 2)  # nosec B101
    assert all(artist.country == "Colombia" for artist in results)  # nosec B101
    assert results[0].name == "Colombian Artist 1"  # nosec B101
    assert results[1].is_verified == True  # nosec B101

    mock_repository.find_by_country.assert_called_once_with("Colombia", 20)

    print("✅ GetArtistsByCountryUseCase funciona correctamente")
    print(f"   - País: Colombia")
    print(f"   - Encontró {len(results)} artistas")
    print(f"   - Artista verificado: {results[1].name}")

    return True


def test_get_popular_artists_use_case():
    """Test GetPopularArtistsUseCase"""
    print("\n🎤 Probando GetPopularArtistsUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Artistas populares (ordenados por seguidores descendente)
    popular_artists = [
        create_mock_artist(
            "pop-1", "Most Popular Artist", followers_count=1000000, is_verified=True
        ),
        create_mock_artist(
            "pop-2", "Second Popular Artist", followers_count=500000, is_verified=True
        ),
        create_mock_artist("pop-3", "Third Popular Artist", followers_count=250000),
    ]

    mock_repository.get_popular_artists.return_value = popular_artists

    # Crear use case
    use_case = GetPopularArtistsUseCase(mock_repository)

    # Ejecutar
    results = use_case.execute(limit=3)

    # Verificaciones
    assert len(results == 3)  # nosec B101
    assert results[0].followers_count == 1000000  # nosec B101
    assert results[1].followers_count == 500000  # nosec B101
    assert results[2].followers_count == 250000  # nosec B101
    for i in range(len(results) - 1):
        assert (
            results[i].followers_count >= results[i + 1].followers_count
        )  # nosec B101

    mock_repository.get_popular_artists.assert_called_once_with(3)

    print("✅ GetPopularArtistsUseCase funciona correctamente")
    print(f"   - Obtuvo {len(results)} artistas populares")
    print(
        f"   - Más popular: {results[0].name} ({results[0].followers_count:,} seguidores)"
    )

    return True


def test_get_verified_artists_use_case():
    """Test GetVerifiedArtistsUseCase"""
    print("\n🎤 Probando GetVerifiedArtistsUseCase...")

    # Crear mock repository
    mock_repository = Mock()

    # Solo artistas verificados
    verified_artists = [
        create_mock_artist(
            "ver-1", "Verified Artist 1", followers_count=80000, is_verified=True
        ),
        create_mock_artist(
            "ver-2", "Verified Artist 2", followers_count=120000, is_verified=True
        ),
        create_mock_artist(
            "ver-3", "Verified Artist 3", followers_count=200000, is_verified=True
        ),
    ]

    mock_repository.get_verified_artists.return_value = verified_artists

    # Crear use case
    use_case = GetVerifiedArtistsUseCase(mock_repository)

    # Ejecutar
    results = use_case.execute(limit=5)

    # Verificaciones
    assert len(results == 3)  # nosec B101
    assert all(artist.is_verified for artist in results)  # nosec B101
    assert results[0].name == "Verified Artist 1"  # nosec B101

    mock_repository.get_verified_artists.assert_called_once_with(5)

    print("✅ GetVerifiedArtistsUseCase funciona correctamente")
    print(f"   - Obtuvo {len(results)} artistas verificados")
    print(f"   - Todos tienen verificación: ✅")

    return True


def test_empty_results():
    """Test casos con resultados vacíos"""
    print("\n🎤 Probando casos con resultados vacíos...")

    # Mock repository que retorna listas vacías
    mock_repository = Mock()
    mock_repository.search_by_name.return_value = []
    mock_repository.find_by_country.return_value = []
    mock_repository.get_popular_artists.return_value = []
    mock_repository.get_verified_artists.return_value = []

    # Test búsqueda sin resultados
    search_use_case = SearchArtistsByNameUseCase(mock_repository)
    search_results = search_use_case.execute("nonexistent")
    assert search_results == []  # nosec B101
    country_use_case = GetArtistsByCountryUseCase(mock_repository)
    country_results = country_use_case.execute("Antarctica")
    assert country_results == []  # nosec B101
    popular_use_case = GetPopularArtistsUseCase(mock_repository)
    popular_results = popular_use_case.execute()
    assert popular_results == []  # nosec B101
    verified_use_case = GetVerifiedArtistsUseCase(mock_repository)
    verified_results = verified_use_case.execute()
    assert verified_results == []  # nosec B101

    print("✅ Casos con resultados vacíos funcionan correctamente")

    return True


def main():
    """Función principal"""
    print("🚀 Iniciando tests directos de Use Cases de Artists...")
    print("=" * 60)

    try:
        # Ejecutar tests
        test_get_artist_use_case()
        test_get_artist_not_found()
        test_get_all_artists_use_case()
        test_search_artists_by_name_use_case()
        test_get_artists_by_country_use_case()
        test_get_popular_artists_use_case()
        test_get_verified_artists_use_case()
        test_empty_results()

        print("\n" + "=" * 60)
        print("🎉 ¡Todos los tests de use cases pasaron correctamente!")
        print("✅ Los casos de uso de Artists funcionan bien")

        return 0

    except Exception as e:
        print(f"\n❌ Error en los tests: {str(e)}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
