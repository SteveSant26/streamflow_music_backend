#!/usr/bin/env python3
"""
Tests para entidades del dominio Genre
"""

import os
import sys
from datetime import datetime
from uuid import uuid4

# Configurar el path correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..")
sys.path.insert(0, project_root)

try:
    # Importar entidades del dominio
    from src.apps.genres.domain.entities import GenreEntity

    print("✅ Entidad GenreEntity importada correctamente")
except ImportError as e:
    print(f"❌ Error importando GenreEntity: {e}")
    sys.exit(1)


def test_genre_entity_creation():
    """Test creación de entidad GenreEntity"""
    print("🎼 Probando creación de GenreEntity...")

    # Datos completos
    genre_data = {
        "id": str(uuid4()),
        "name": "Rock",
        "description": "Género musical caracterizado por el uso de guitarras eléctricas",
        "image_url": "https://example.com/rock.jpg",
        "color_hex": "#FF6B35",
        "popularity_score": 85,
        "is_active": True,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Crear entidad
    genre = GenreEntity(**genre_data)

    # Verificaciones
    assert genre.id == genre_data["id"]
    assert genre.name == "Rock"
    assert (
        genre.description
        == "Género musical caracterizado por el uso de guitarras eléctricas"
    )
    assert genre.image_url == "https://example.com/rock.jpg"
    assert genre.color_hex == "#FF6B35"
    assert genre.popularity_score == 85
    assert genre.is_active == True

    print("✅ GenreEntity se crea correctamente con datos completos")
    print(f"   - Nombre: {genre.name}")
    print(f"   - Descripción: {genre.description[:50]}...")
    print(f"   - Color: {genre.color_hex}")
    print(f"   - Popularidad: {genre.popularity_score}")


def test_genre_entity_minimal_data():
    """Test creación de GenreEntity con datos mínimos"""
    print("🎼 Probando GenreEntity con datos mínimos...")

    # Datos mínimos requeridos
    minimal_data = {"id": str(uuid4()), "name": "Jazz"}

    # Crear entidad
    genre = GenreEntity(**minimal_data)

    # Verificaciones
    assert genre.id == minimal_data["id"]
    assert genre.name == "Jazz"

    # Valores por defecto
    assert genre.description is None
    assert genre.image_url is None
    assert genre.color_hex is None
    assert genre.popularity_score == 0
    assert genre.is_active == True
    assert genre.created_at is None
    assert genre.updated_at is None

    print("✅ GenreEntity se crea correctamente con datos mínimos")
    print(f"   - Nombre: {genre.name}")
    print(f"   - ID: {genre.id[:8]}...")
    print(f"   - Activo por defecto: {genre.is_active}")


def test_genre_entity_properties():
    """Test propiedades de GenreEntity"""
    print("🎼 Probando propiedades de GenreEntity...")

    genre = GenreEntity(
        id="genre-123",
        name="Electronic",
        description="Música electrónica y sintética",
        color_hex="#00D4FF",
        popularity_score=92,
        is_active=True,
    )

    # Verificar propiedades
    assert genre.name == "Electronic"
    assert genre.description == "Música electrónica y sintética"
    assert genre.color_hex == "#00D4FF"
    assert genre.popularity_score == 92
    assert genre.is_active == True

    print("✅ Propiedades de GenreEntity funcionan correctamente")
    print(f"   - Género: {genre.name}")
    print(f"   - Popularidad: {genre.popularity_score}")
    print(f"   - Color: {genre.color_hex}")
    print(f"   - Descripción: {genre.description}")


def test_genre_entity_string_representation():
    """Test representación string de GenreEntity"""
    print("🎼 Probando representación string...")

    genre = GenreEntity(
        id="genre-456",
        name="Classical",
        description="Música clásica tradicional",
        color_hex="#8B4513",
        popularity_score=68,
    )

    # Verificar representación string
    genre_str = str(genre)

    assert "GenreEntity" in genre_str
    assert "Classical" in genre_str
    assert "genre-456" in genre_str

    print("✅ Representación string funciona")
    print(f"   - String: {genre_str}")


def test_genre_entity_equality():
    """Test igualdad de entidades GenreEntity"""
    print("🎼 Probando igualdad de entidades...")

    # Crear dos géneros con el mismo ID
    genre1 = GenreEntity(id="same-id", name="Pop", popularity_score=90)

    genre2 = GenreEntity(
        id="same-id",
        name="Pop Music",  # Nombre diferente
        popularity_score=85,  # Popularidad diferente
    )

    # Crear género con ID diferente
    genre3 = GenreEntity(id="different-id", name="Pop")

    # Verificar igualdad (las dataclasses comparan todos los campos por defecto)
    # Como tienen diferentes datos, no serán iguales aunque tengan mismo ID
    assert genre1 != genre2, "Géneros con diferentes datos deberían ser diferentes"
    assert genre1 != genre3, "Géneros con diferente ID deberían ser diferentes"

    # Crear géneros idénticos
    genre4 = GenreEntity(id="identical-id", name="Identical", popularity_score=100)

    genre5 = GenreEntity(id="identical-id", name="Identical", popularity_score=100)

    assert genre4 == genre5, "Géneros idénticos deberían ser iguales"

    print("✅ Igualdad de entidades funciona correctamente")
    print(f"   - Diferentes datos: {genre1 != genre2}")
    print(f"   - Diferente ID: {genre1 != genre3}")
    print(f"   - Idénticos: {genre4 == genre5}")


def run_all_tests():
    """Ejecutar todos los tests de entidades Genre"""
    print("🧪 TESTS DE ENTIDADES GENRE")
    print("=" * 50)

    tests = [
        test_genre_entity_creation,
        test_genre_entity_minimal_data,
        test_genre_entity_properties,
        test_genre_entity_string_representation,
        test_genre_entity_equality,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ Error en {test.__name__}: {e}")
            failed += 1

    print("=" * 50)
    print(f"📊 RESULTADOS: {passed} pasaron, {failed} fallaron")

    if failed == 0:
        print("🎉 ¡Todos los tests de entidades Genre pasaron!")
    else:
        print("⚠️ Algunos tests fallaron")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
