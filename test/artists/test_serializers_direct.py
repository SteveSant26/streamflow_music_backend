#!/usr/bin/env python
"""
Test directo para verificar que los serializers de Artists funcionan
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
from apps.artists.api.serializers.artist_serializers import (
    ArtistResponseSerializer,
    CreateArtistSerializer,
    UpdateArtistSerializer,
)
from apps.artists.domain.entities import ArtistEntity


def test_artist_response_serializer():
    """Test ArtistResponseSerializer con entidad"""
    print("🎤 Probando ArtistResponseSerializer...")

    # Crear entidad de artista
    artist_entity = ArtistEntity(
        id="test-artist-123",
        name="Test Response Artist",
        biography="Una biografía de prueba para serializer",
        country="Colombia",
        image_url="https://example.com/response-artist.jpg",
        followers_count=85000,
        is_verified=True,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Serializar entidad
    serializer = ArtistResponseSerializer(artist_entity)
    data = serializer.data

    # Verificaciones
    assert data["id"] == "test-artist-123"
    assert data["name"] == "Test Response Artist"
    assert data["biography"] == "Una biografía de prueba para serializer"
    assert data["country"] == "Colombia"
    assert data["image_url"] == "https://example.com/response-artist.jpg"
    assert data["followers_count"] == 85000
    assert data["is_verified"] == True
    assert data["is_active"] == True
    assert "created_at" in data
    assert "updated_at" in data

    print("✅ ArtistResponseSerializer funciona correctamente")
    print(f"   - ID: {data['id']}")
    print(f"   - Nombre: {data['name']}")
    print(f"   - País: {data['country']}")
    print(f"   - Seguidores: {data['followers_count']:,}")
    print(f"   - Verificado: {data['is_verified']}")

    return True


def test_create_artist_serializer_valid():
    """Test CreateArtistSerializer con datos válidos"""
    print("\n🎤 Probando CreateArtistSerializer con datos válidos...")

    # Datos válidos para crear artista
    create_data = {
        "name": "New Artist to Create",
        "biography": "Biografía del nuevo artista",
        "country": "México",
        "image_url": "https://example.com/new-artist.jpg",
    }

    # Crear serializer
    serializer = CreateArtistSerializer(data=create_data)

    # Verificar que es válido
    is_valid = serializer.is_valid()
    if not is_valid:
        print(f"   Errores: {serializer.errors}")
        return False

    assert is_valid == True

    # Verificar datos validados
    validated_data = serializer.validated_data
    assert validated_data["name"] == "New Artist to Create"
    assert validated_data["biography"] == "Biografía del nuevo artista"
    assert validated_data["country"] == "México"
    assert validated_data["image_url"] == "https://example.com/new-artist.jpg"

    print("✅ CreateArtistSerializer funciona correctamente")
    print(f"   - Nombre: {validated_data['name']}")
    print(f"   - País: {validated_data['country']}")
    print(f"   - Biografía: {validated_data['biography'][:50]}...")

    return True


def test_create_artist_serializer_minimal():
    """Test CreateArtistSerializer con datos mínimos"""
    print("\n🎤 Probando CreateArtistSerializer con datos mínimos...")

    # Solo campo requerido
    minimal_data = {"name": "Minimal New Artist"}

    # Crear serializer
    serializer = CreateArtistSerializer(data=minimal_data)

    # Verificar que es válido
    is_valid = serializer.is_valid()
    assert is_valid == True

    # Verificar datos
    validated_data = serializer.validated_data
    assert validated_data["name"] == "Minimal New Artist"

    # Los campos opcionales no deberían estar presentes si no se enviaron
    assert "biography" not in validated_data or validated_data.get("biography") is None
    assert "country" not in validated_data or validated_data.get("country") is None
    assert "image_url" not in validated_data or validated_data.get("image_url") is None

    print("✅ CreateArtistSerializer mínimo funciona correctamente")
    print(f"   - Solo nombre requerido: {validated_data['name']}")

    return True


def test_create_artist_serializer_validation():
    """Test validaciones de CreateArtistSerializer"""
    print("\n🎤 Probando validaciones de CreateArtistSerializer...")

    # Test campo requerido faltante
    invalid_data = {
        "biography": "Biografía sin nombre",
        "country": "Test Country"
        # Falta 'name' (requerido)
    }

    serializer = CreateArtistSerializer(data=invalid_data)
    is_valid = serializer.is_valid()

    assert is_valid == False
    assert "name" in serializer.errors

    # Test URL inválida
    invalid_url_data = {
        "name": "Artist with Invalid URL",
        "image_url": "not-a-valid-url",
    }

    serializer_url = CreateArtistSerializer(data=invalid_url_data)
    is_valid_url = serializer_url.is_valid()

    assert is_valid_url == False
    assert "image_url" in serializer_url.errors

    # Test nombre muy largo
    long_name_data = {"name": "A" * 300}  # Más largo que max_length=200

    serializer_long = CreateArtistSerializer(data=long_name_data)
    is_valid_long = serializer_long.is_valid()

    assert is_valid_long == False
    assert "name" in serializer_long.errors

    print("✅ Validaciones de CreateArtistSerializer funcionan correctamente")
    print("   - Detecta nombre faltante")
    print("   - Detecta URL inválida")
    print("   - Detecta nombre muy largo")

    return True


def test_update_artist_serializer():
    """Test UpdateArtistSerializer"""
    print("\n🎤 Probando UpdateArtistSerializer...")

    # Datos para actualización (todos opcionales)
    update_data = {
        "name": "Updated Artist Name",
        "biography": "Biografía actualizada",
        "country": "Argentina",
        "image_url": "https://example.com/updated-artist.jpg",
        "followers_count": 120000,
        "is_verified": True,
    }

    # Crear serializer
    serializer = UpdateArtistSerializer(data=update_data)

    # Verificar que es válido
    is_valid = serializer.is_valid()
    if not is_valid:
        print(f"   Errores: {serializer.errors}")
        return False

    assert is_valid == True

    # Verificar datos validados
    validated_data = serializer.validated_data
    assert validated_data["name"] == "Updated Artist Name"
    assert validated_data["biography"] == "Biografía actualizada"
    assert validated_data["country"] == "Argentina"
    assert validated_data["followers_count"] == 120000
    assert validated_data["is_verified"] == True

    print("✅ UpdateArtistSerializer funciona correctamente")
    print(f"   - Nuevo nombre: {validated_data['name']}")
    print(f"   - Nuevos seguidores: {validated_data['followers_count']:,}")
    print(f"   - Verificado: {validated_data['is_verified']}")

    return True


def test_update_artist_serializer_partial():
    """Test UpdateArtistSerializer con actualización parcial"""
    print("\n🎤 Probando UpdateArtistSerializer parcial...")

    # Solo algunos campos para actualizar
    partial_data = {"followers_count": 75000, "is_verified": True}

    # Crear serializer
    serializer = UpdateArtistSerializer(data=partial_data)

    # Verificar que es válido
    is_valid = serializer.is_valid()
    assert is_valid == True

    # Verificar datos
    validated_data = serializer.validated_data
    assert validated_data["followers_count"] == 75000
    assert validated_data["is_verified"] == True

    # Los campos no enviados no deberían estar presentes
    assert "name" not in validated_data
    assert "biography" not in validated_data
    assert "country" not in validated_data

    print("✅ UpdateArtistSerializer parcial funciona correctamente")
    print(f"   - Solo campos específicos actualizados")

    return True


def test_update_artist_serializer_validation():
    """Test validaciones de UpdateArtistSerializer"""
    print("\n🎤 Probando validaciones de UpdateArtistSerializer...")

    # Test followers_count negativo
    negative_data = {"followers_count": -5000}

    serializer = UpdateArtistSerializer(data=negative_data)
    is_valid = serializer.is_valid()

    assert is_valid == False
    assert "followers_count" in serializer.errors

    # Test URL inválida
    invalid_url_data = {"image_url": "invalid-url-format"}

    serializer_url = UpdateArtistSerializer(data=invalid_url_data)
    is_valid_url = serializer_url.is_valid()

    assert is_valid_url == False
    assert "image_url" in serializer_url.errors

    print("✅ Validaciones de UpdateArtistSerializer funcionan correctamente")
    print("   - Detecta seguidores negativos")
    print("   - Detecta URL inválida")

    return True


def test_serializers_with_none_values():
    """Test serializers con valores None/nulos"""
    print("\n🎤 Probando serializers con valores None...")

    # CreateArtistSerializer con campos nulos
    create_data = {
        "name": "Artist with Nulls",
        "biography": None,
        "country": None,
        "image_url": None,
    }

    create_serializer = CreateArtistSerializer(data=create_data)
    assert create_serializer.is_valid() == True

    # UpdateArtistSerializer con campos nulos
    update_data = {
        "name": "Updated with Nulls",
        "biography": None,
        "country": None,
        "image_url": None,
    }

    update_serializer = UpdateArtistSerializer(data=update_data)
    assert update_serializer.is_valid() == True

    print("✅ Serializers con valores None funcionan correctamente")
    print("   - Campos opcionales aceptan None")

    return True


def test_serializers_with_empty_strings():
    """Test serializers con strings vacíos"""
    print("\n🎤 Probando serializers con strings vacíos...")

    # Datos con strings vacíos
    empty_data = {
        "name": "Artist with Empty Strings",
        "biography": "",
        "country": "",
        "image_url": "",
    }

    # CreateArtistSerializer
    create_serializer = CreateArtistSerializer(data=empty_data)
    assert create_serializer.is_valid() == True

    # UpdateArtistSerializer
    update_serializer = UpdateArtistSerializer(data=empty_data)
    assert update_serializer.is_valid() == True

    print("✅ Serializers con strings vacíos funcionan correctamente")
    print("   - Campos opcionales aceptan strings vacíos")

    return True


def main():
    """Función principal"""
    print("🚀 Iniciando tests directos de serializers de Artists...")
    print("=" * 70)

    try:
        # Ejecutar tests
        test_artist_response_serializer()
        test_create_artist_serializer_valid()
        test_create_artist_serializer_minimal()
        test_create_artist_serializer_validation()
        test_update_artist_serializer()
        test_update_artist_serializer_partial()
        test_update_artist_serializer_validation()
        test_serializers_with_none_values()
        test_serializers_with_empty_strings()

        print("\n" + "=" * 70)
        print("🎉 ¡Todos los tests de serializers pasaron correctamente!")
        print("✅ Los serializers de Artists funcionan bien")

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
