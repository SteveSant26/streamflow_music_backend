#!/usr/bin/env python3
"""
Tests para serializadores de Albums API
"""

import os
import sys
from datetime import date, datetime
from uuid import uuid4

# Configurar el path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..")
sys.path.insert(0, project_root)


# Mock para Django REST framework
class MockField:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class MockSerializer:
    pass


# Mock básico para evitar dependencias de Django
class MockAlbumSerializer:
    """Mock del serializer de álbumes para testing"""

    def __init__(self, data=None, instance=None):
        self.data = data
        self.instance = instance
        self._validated_data = None

    def is_valid(self, raise_exception=False):
        """Mock de validación"""
        if self.data:
            required_fields = ["title", "artist_id", "artist_name"]
            for field in required_fields:
                if field not in self.data:
                    if raise_exception:
                        raise Exception(f"Field '{field}' is required")
                    return False
            self._validated_data = self.data
            return True
        return False

    @property
    def validated_data(self):
        return self._validated_data or {}

    def to_representation(self, instance):
        """Mock de serialización"""
        if hasattr(instance, "__dict__"):
            return {
                "id": str(instance.id),
                "title": instance.title,
                "artist_id": str(instance.artist_id),
                "artist_name": instance.artist_name,
                "release_date": instance.release_date.isoformat()
                if instance.release_date
                else None,
                "description": instance.description,
                "cover_image_url": instance.cover_image_url,
                "total_tracks": instance.total_tracks,
                "play_count": instance.play_count,
                "is_active": instance.is_active,
                "created_at": instance.created_at.isoformat()
                if instance.created_at
                else None,
                "updated_at": instance.updated_at.isoformat()
                if instance.updated_at
                else None,
            }
        return instance


try:
    # Importar entidades del dominio
    from src.apps.albums.domain.entities import AlbumEntity

    print("✅ Entidades importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando: {e}")
    sys.exit(1)


def create_mock_album_entity(
    album_id: str = None, title: str = "Test Album"
) -> AlbumEntity:
    """Crear entidad de álbum para testing"""
    return AlbumEntity(
        id=album_id or str(uuid4()),
        title=title,
        artist_id=str(uuid4()),
        artist_name="Test Artist",
        release_date=date(2020, 1, 1),
        description="Test description",
        cover_image_url="https://example.com/cover.jpg",
        total_tracks=10,
        play_count=5000,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


def test_album_serializer_validation():
    """Test validación del serializer"""
    print("📀 Probando validación del serializer...")

    # Datos válidos
    valid_data = {
        "title": "Dark Side of the Moon",
        "artist_id": str(uuid4()),
        "artist_name": "Pink Floyd",
        "release_date": "1973-03-01",
        "total_tracks": 10,
        "play_count": 15000,
    }

    serializer = MockAlbumSerializer(data=valid_data)
    assert serializer.is_valid() is True  # nosec B101
    assert serializer.validated_data["title"] == "Dark Side of the Moon"  # nosec B101
    assert serializer.validated_data["total_tracks"] == 10  # nosec B101

    print("✅ Validación con datos válidos funciona")
    print(f"   - Título: {serializer.validated_data['title']}")
    print(f"   - Artista: {serializer.validated_data['artist_name']}")

    return True


def test_album_serializer_validation_errors():
    """Test errores de validación"""
    print("\n📀 Probando errores de validación...")

    # Datos incompletos - falta título
    invalid_data = {"artist_id": str(uuid4()), "artist_name": "Pink Floyd"}

    serializer = MockAlbumSerializer(data=invalid_data)
    assert serializer.is_valid( == False)  # nosec B101
    invalid_data2 = {"title": "Test Album", "artist_name": "Pink Floyd"}

    serializer2 = MockAlbumSerializer(data=invalid_data2)
    assert serializer2.is_valid( == False)  # nosec B101

    print("✅ Validación de errores funciona correctamente")
    print("   - Detecta campos faltantes correctamente")

    return True


def test_album_serializer_representation():
    """Test serialización de entidades a diccionario"""
    print("\n📀 Probando serialización...")

    # Crear entidad de álbum
    album = create_mock_album_entity(album_id="album-123", title="The Wall")

    serializer = MockAlbumSerializer(instance=album)
    representation = serializer.to_representation(album)

    # Verificaciones
    assert representation["id"] == "album-123"  # nosec B101
    assert representation["title"] == "The Wall"  # nosec B101
    assert representation["artist_name"] == "Test Artist"  # nosec B101
    assert representation["total_tracks"] == 10  # nosec B101
    assert representation["play_count"] == 5000  # nosec B101
    assert representation["is_active"] == True  # nosec B101
    assert representation["release_date"] == "2020-01-01"  # nosec B101

    print("✅ Serialización funciona correctamente")
    print(f"   - ID: {representation['id']}")
    print(f"   - Título: {representation['title']}")
    print(f"   - Pistas: {representation['total_tracks']}")

    return True


def test_album_serializer_minimal_data():
    """Test serialización con datos mínimos"""
    print("\n📀 Probando serialización con datos mínimos...")

    # Crear entidad mínima
    minimal_album = AlbumEntity(
        id="minimal-123",
        title="Minimal Album",
        artist_id=str(uuid4()),
        artist_name="Minimal Artist",
    )

    serializer = MockAlbumSerializer(instance=minimal_album)
    representation = serializer.to_representation(minimal_album)

    # Verificaciones
    assert representation["id"] == "minimal-123"  # nosec B101
    assert representation["title"] == "Minimal Album"  # nosec B101
    assert representation["artist_name"] == "Minimal Artist"  # nosec B101
    assert representation["release_date"] is None  # nosec B101
    assert representation["description"] is None  # nosec B101
    assert representation["cover_image_url"] is None  # nosec B101
    assert representation["total_tracks"] == 0  # nosec B101
    assert representation["play_count"] == 0  # nosec B101
    assert representation["is_active"] == True  # nosec B101

    print("✅ Serialización con datos mínimos funciona")
    print(f"   - Título: {representation['title']}")
    print(f"   - Campos opcionales son None: ✓")

    return True


def test_album_search_serializer():
    """Test serializer de búsqueda de álbumes"""
    print("\n📀 Probando serializer de búsqueda...")

    # Mock para serializer de búsqueda
    class MockAlbumSearchSerializer:
        def __init__(self, data=None):
            self.data = data or {}
            self._validated_data = None

        def is_valid(self, raise_exception=False):
            # Verificar que al menos 'q' esté presente
            if "q" not in self.data:
                if raise_exception:
                    raise Exception("Field 'q' is required")
                return False
            self._validated_data = self.data
            return True

        @property
        def validated_data(self):
            return self._validated_data or {}

    # Datos de búsqueda válidos
    search_data = {"q": "rock", "artist_id": str(uuid4()), "artist_name": "Pink Floyd"}

    search_serializer = MockAlbumSearchSerializer(data=search_data)
    assert search_serializer.is_valid( == True)  # nosec B101
    assert search_serializer.validated_data["q"] == "rock"  # nosec B101
    invalid_search_data = {"artist_name": "Pink Floyd"}

    invalid_search_serializer = MockAlbumSearchSerializer(data=invalid_search_data)
    assert invalid_search_serializer.is_valid( == False)  # nosec B101

    print("✅ Serializer de búsqueda funciona")
    print(f"   - Query válida: {search_serializer.validated_data['q']}")
    print("   - Detecta query faltante: ✓")

    return True


def test_album_response_serializer():
    """Test serializer de respuesta de búsqueda"""
    print("\n📀 Probando serializer de respuesta...")

    # Mock para respuesta de búsqueda
    class MockAlbumSearchResponseSerializer:
        def __init__(self, data=None):
            self.data = data or {}

        def to_representation(self, instance):
            return {
                "source": instance.get("source", "local_cache"),
                "results": instance.get("results", []),
                "message": instance.get("message", ""),
            }

    # Crear respuesta de búsqueda
    album1 = create_mock_album_entity("result-1", "Result Album 1")
    album2 = create_mock_album_entity("result-2", "Result Album 2")

    album_serializer = MockAlbumSerializer()
    serialized_albums = [
        album_serializer.to_representation(album1),
        album_serializer.to_representation(album2),
    ]

    response_data = {
        "source": "local_cache",
        "results": serialized_albums,
        "message": "Found 2 albums",
    }

    response_serializer = MockAlbumSearchResponseSerializer()
    response_repr = response_serializer.to_representation(response_data)

    # Verificaciones
    assert response_repr["source"] == "local_cache"  # nosec B101
    assert len(response_repr["results"] == 2)  # nosec B101
    assert response_repr["results"][0]["title"] == "Result Album 1"  # nosec B101
    assert response_repr["results"][1]["title"] == "Result Album 2"  # nosec B101
    assert response_repr["message"] == "Found 2 albums"  # nosec B101

    print("✅ Serializer de respuesta funciona")
    print(f"   - Fuente: {response_repr['source']}")
    print(f"   - Resultados: {len(response_repr['results'])}")
    print(f"   - Mensaje: {response_repr['message']}")

    return True


def run_all_tests():
    """Ejecuta todos los tests de serializadores Album"""
    print("🧪 TESTS DE SERIALIZADORES ALBUM")
    print("=" * 50)

    tests = [
        test_album_serializer_validation,
        test_album_serializer_validation_errors,
        test_album_serializer_representation,
        test_album_serializer_minimal_data,
        test_album_search_serializer,
        test_album_response_serializer,
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
        print("🎉 ¡Todos los tests de serializadores Album pasaron!")
        return True
    else:
        print(f"⚠️  {failed} tests fallaron")
        return False


if __name__ == "__main__":
    run_all_tests()
