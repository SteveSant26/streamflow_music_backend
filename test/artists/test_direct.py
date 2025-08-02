#!/usr/bin/env python
"""
Test directo para verificar que las entidades de Artists funcionan
"""
import os
import sys
from datetime import datetime
from pathlib import Path

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


def test_artist_entity_creation():
    """Test creación básica de ArtistEntity"""
    print("🎤 Probando creación de ArtistEntity...")

    # Crear entidad con datos completos
    artist = ArtistEntity(
        id="artist-test-123",
        name="Test Artist",
        biography="Una biografía de prueba para el artista",
        country="Colombia",
        image_url="https://example.com/artist.jpg",
        followers_count=50000,
        is_verified=True,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Verificaciones
    assert artist.id == "artist-test-123"  # nosec B101
    assert artist.name == "Test Artist"  # nosec B101
    assert artist.biography == "Una biografía de prueba para el artista"  # nosec B101
    assert artist.country == "Colombia"  # nosec B101
    assert artist.image_url == "https://example.com/artist.jpg"  # nosec B101
    assert artist.followers_count == 50000  # nosec B101
    assert artist.is_verified == True  # nosec B101
    assert artist.is_active == True  # nosec B101
    assert artist.created_at is not None  # nosec B101
    assert artist.updated_at is not None  # nosec B101

    print("✅ ArtistEntity creada correctamente")
    print(f"   - ID: {artist.id}")
    print(f"   - Nombre: {artist.name}")
    print(f"   - País: {artist.country}")
    print(f"   - Seguidores: {artist.followers_count:,}")
    print(f"   - Verificado: {artist.is_verified}")

    return True


def test_artist_entity_minimal():
    """Test creación de ArtistEntity con datos mínimos"""
    print("\n🎤 Probando ArtistEntity con datos mínimos...")

    # Crear entidad solo con campos requeridos
    artist = ArtistEntity(id="minimal-artist-456", name="Minimal Artist")

    # Verificar campos requeridos
    assert artist.id == "minimal-artist-456"  # nosec B101
    assert artist.name == "Minimal Artist"  # nosec B101
    assert artist.biography is None  # nosec B101
    assert artist.country is None  # nosec B101
    assert artist.image_url is None  # nosec B101
    assert artist.followers_count == 0  # nosec B101
    assert artist.is_verified == False  # nosec B101
    assert artist.is_active == True  # nosec B101
    assert artist.created_at is None  # nosec B101
    assert artist.updated_at is None  # nosec B101

    print("✅ ArtistEntity mínima creada correctamente")
    print(f"   - Solo campos requeridos: ID y name")
    print(f"   - Valores por defecto aplicados correctamente")

    return True


def test_artist_entity_country_variations():
    """Test diferentes valores de país"""
    print("\n🎤 Probando variaciones de país...")

    countries = [
        "Colombia",
        "Mexico",
        "Argentina",
        "España",
        "Estados Unidos",
        "Brasil",
        None,
    ]

    for i, country in enumerate(countries):
        artist = ArtistEntity(
            id=f"artist-country-{i}",
            name=f'Artist from {country or "Unknown"}',
            country=country,
        )

        assert artist.country == country  # nosec B101

        if country:
            print(f"   - Artista de {country}: ✅")
        else:
            print(f"   - Artista sin país especificado: ✅")

    print("✅ Variaciones de país funcionan correctamente")

    return True


def test_artist_entity_verification_status():
    """Test estados de verificación"""
    print("\n🎤 Probando estados de verificación...")

    # Artista no verificado
    unverified = ArtistEntity(
        id="unverified-artist", name="Unverified Artist", is_verified=False
    )

    # Artista verificado
    verified = ArtistEntity(
        id="verified-artist",
        name="Verified Artist",
        is_verified=True,
        followers_count=100000,
    )

    assert unverified.is_verified == False  # nosec B101
    assert verified.is_verified == True  # nosec B101

    print("✅ Estados de verificación funcionan correctamente")
    print(f"   - Artista no verificado: {unverified.name}")
    print(f"   - Artista verificado: {verified.name}")

    return True


def test_artist_entity_followers_count():
    """Test contadores de seguidores"""
    print("\n🎤 Probando contadores de seguidores...")

    test_cases = [
        (0, "Artista nuevo"),
        (1000, "Artista emergente"),
        (50000, "Artista establecido"),
        (1000000, "Artista popular"),
        (10000000, "Artista internacional"),
    ]

    for followers, description in test_cases:
        artist = ArtistEntity(
            id=f"artist-followers-{followers}",
            name=f"Artist with {followers} followers",
            followers_count=followers,
        )

        assert artist.followers_count == followers  # nosec B101
        print(f"   - {description}: {followers:,} seguidores ✅")

    print("✅ Contadores de seguidores funcionan correctamente")

    return True


def main():
    """Función principal"""
    print("🚀 Iniciando tests directos de Artists...")
    print("=" * 50)

    try:
        # Ejecutar tests
        test_artist_entity_creation()
        test_artist_entity_minimal()
        test_artist_entity_country_variations()
        test_artist_entity_verification_status()
        test_artist_entity_followers_count()

        print("\n" + "=" * 50)
        print("🎉 ¡Todos los tests pasaron correctamente!")
        print("✅ Las entidades de Artists funcionan bien")

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
