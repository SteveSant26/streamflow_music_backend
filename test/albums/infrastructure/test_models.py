#!/usr/bin/env python3
"""
Tests para modelos de infrastructura Albums
"""

import os
import sys
from datetime import date, datetime
from uuid import uuid4

# Configurar el path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, "..", "..", "..")
sys.path.insert(0, project_root)


# Mock del modelo Django para evitar dependencias
class MockAlbumModel:
    """Mock del modelo Django para testing"""

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", uuid4())
        self.title = kwargs.get("title", "")
        self.artist_id = kwargs.get("artist_id", uuid4())
        self.artist_name = kwargs.get("artist_name", "")
        self.release_date = kwargs.get("release_date")
        self.description = kwargs.get("description", "")
        self.cover_image_url = kwargs.get("cover_image_url", "")
        self.total_tracks = kwargs.get("total_tracks", 0)
        self.play_count = kwargs.get("play_count", 0)
        self.is_active = kwargs.get("is_active", True)
        self.created_at = kwargs.get("created_at", datetime.now())
        self.updated_at = kwargs.get("updated_at", datetime.now())

        # Mock del manager
        self.objects = MockManager()

    def save(self):
        """Mock del método save"""
        self.updated_at = datetime.now()
        return self

    def refresh_from_db(self):
        """Mock del método refresh_from_db"""

    def __str__(self):
        return f"{self.title} - {self.artist_name}"


class MockManager:
    """Mock del manager de Django"""

    def __init__(self):
        self._objects = []

    def create(self, **kwargs):
        """Mock del método create"""
        obj = MockAlbumModel(**kwargs)
        self._objects.append(obj)
        return obj

    def all(self):
        """Mock del método all"""
        return MockQuerySet(self._objects)

    def filter(self, **kwargs):
        """Mock del método filter"""
        filtered = []
        for obj in self._objects:
            match = True
            for key, value in kwargs.items():
                if "__icontains" in key:
                    field_name = key.split("__")[0]
                    if not hasattr(obj, field_name):
                        match = False
                        break
                    field_value = getattr(obj, field_name)
                    if value.lower() not in field_value.lower():
                        match = False
                        break
                else:
                    if not hasattr(obj, key):
                        match = False
                        break
                    if getattr(obj, key) != value:
                        match = False
                        break
            if match:
                filtered.append(obj)
        return MockQuerySet(filtered)


class MockQuerySet:
    """Mock del QuerySet de Django"""

    def __init__(self, objects=None):
        self._objects = objects or []

    def count(self):
        return len(self._objects)

    def exists(self):
        return len(self._objects) > 0

    def first(self):
        return self._objects[0] if self._objects else None

    def __getitem__(self, key):
        return self._objects[key]

    def __len__(self):
        return len(self._objects)

    def __iter__(self):
        return iter(self._objects)


try:
    # Importar entidad del dominio
    from src.apps.albums.domain.entities import AlbumEntity

    print("✅ Entidades importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando: {e}")
    sys.exit(1)


def test_album_model_creation():
    """Test creación de modelo AlbumModel"""
    print("📀 Probando creación de MockAlbumModel...")

    # Mock del manager global
    MockAlbumModel.objects = MockManager()

    # Crear álbum con datos completos
    album = MockAlbumModel.objects.create(
        id=uuid4(),
        title="Dark Side of the Moon",
        artist_id=uuid4(),
        artist_name="Pink Floyd",
        release_date=date(1973, 3, 1),
        description="Progressive rock masterpiece",
        cover_image_url="https://example.com/cover.jpg",
        total_tracks=10,
        play_count=15000,
    )

    # Verificaciones
    assert album.id is not None  # nosec B101
    assert album.title == "Dark Side of the Moon"  # nosec B101
    assert album.artist_name == "Pink Floyd"  # nosec B101
    assert album.total_tracks == 10  # nosec B101
    assert album.play_count == 15000  # nosec B101
    assert album.is_active == True  # nosec B101
    assert album.created_at is not None  # nosec B101
    assert album.updated_at is not None  # nosec B101

    print("✅ MockAlbumModel se crea correctamente")
    print(f"   - Título: {album.title}")
    print(f"   - Artista: {album.artist_name}")
    print(f"   - Pistas: {album.total_tracks}")

    return True


def test_album_model_minimal_data():
    """Test creación de modelo con datos mínimos"""
    print("\n📀 Probando MockAlbumModel con datos mínimos...")

    # Mock del manager
    MockAlbumModel.objects = MockManager()

    # Crear álbum solo con campos requeridos
    album = MockAlbumModel.objects.create(
        id=uuid4(), title="Abbey Road", artist_id=uuid4(), artist_name="The Beatles"
    )

    # Verificaciones
    assert album.title == "Abbey Road"  # nosec B101
    assert album.artist_name == "The Beatles"  # nosec B101
    assert album.release_date is None  # nosec B101
    assert album.description == ""  # nosec B101
    assert album.cover_image_url == ""  # nosec B101
    assert album.total_tracks == 0  # nosec B101
    assert album.play_count == 0  # nosec B101
    assert album.is_active == True  # nosec B101

    print("✅ MockAlbumModel se crea correctamente con datos mínimos")
    print(f"   - Título: {album.title}")
    print(f"   - Artista: {album.artist_name}")
    print(f"   - Activo por defecto: {album.is_active}")

    return True


def test_album_model_string_representation():
    """Test representación string del modelo"""
    print("\n📀 Probando representación string del modelo...")

    album = MockAlbumModel(
        id=uuid4(), title="Thriller", artist_id=uuid4(), artist_name="Michael Jackson"
    )

    str_repr = str(album)
    expected = "Thriller - Michael Jackson"

    assert str_repr == expected  # nosec B101

    print("✅ Representación string funciona correctamente")
    print(f"   - String: {str_repr}")

    return True


def test_album_model_queries():
    """Test consultas del modelo"""
    print("\n📀 Probando consultas del modelo...")

    # Mock del manager con datos
    MockAlbumModel.objects = MockManager()

    # Crear varios álbumes para testing
    albums_data = [
        {
            "id": uuid4(),
            "title": "The Wall",
            "artist_id": uuid4(),
            "artist_name": "Pink Floyd",
            "total_tracks": 26,
            "play_count": 10000,
        },
        {
            "id": uuid4(),
            "title": "Hotel California",
            "artist_id": uuid4(),
            "artist_name": "Eagles",
            "total_tracks": 9,
            "play_count": 20000,
        },
        {
            "id": uuid4(),
            "title": "Bohemian Rhapsody",
            "artist_id": uuid4(),
            "artist_name": "Queen",
            "total_tracks": 12,
            "play_count": 30000,
            "is_active": False,  # Inactivo para testing
        },
    ]

    created_albums = []
    for data in albums_data:
        album = MockAlbumModel.objects.create(**data)
        created_albums.append(album)

    # Test consultas básicas
    all_albums = MockAlbumModel.objects.all()
    active_albums = MockAlbumModel.objects.filter(is_active=True)
    inactive_albums = MockAlbumModel.objects.filter(is_active=False)

    assert all_albums.count( >= 3)  # nosec B101
    assert active_albums.count( >= 2)  # nosec B101
    assert inactive_albums.count( >= 1)  # nosec B101
    wall_albums = MockAlbumModel.objects.filter(title__icontains="Wall")
    assert wall_albums.count( >= 1)  # nosec B101
    assert wall_albums.first(.title == "The Wall")  # nosec B101

    print("✅ Consultas del modelo funcionan correctamente")
    print(f"   - Total álbumes: {all_albums.count()}")
    print(f"   - Álbumes activos: {active_albums.count()}")
    print(f"   - Álbumes inactivos: {inactive_albums.count()}")

    return True


def test_album_model_updates():
    """Test actualizaciones del modelo"""
    print("\n📀 Probando actualizaciones del modelo...")

    # Crear álbum
    album = MockAlbumModel(
        id=uuid4(),
        title="Original Title",
        artist_id=uuid4(),
        artist_name="Original Artist",
        play_count=1000,
    )

    original_updated_at = album.updated_at

    # Esperar un momento para que el timestamp sea diferente
    import time

    time.sleep(0.01)

    # Actualizar álbum
    album.title = "Updated Title"
    album.play_count = 2000
    album.save()

    # Simular refresh_from_db
    album.refresh_from_db()

    # Verificaciones
    assert album.title == "Updated Title"  # nosec B101
    assert album.play_count == 2000  # nosec B101
    assert album.updated_at > original_updated_at  # nosec B101

    print("✅ Actualizaciones del modelo funcionan correctamente")
    print(f"   - Título actualizado: {album.title}")
    print(f"   - Play count actualizado: {album.play_count}")

    return True


def test_model_to_entity_conversion():
    """Test conversión de modelo a entidad"""
    print("\n📀 Probando conversión modelo a entidad...")

    # Crear modelo mock
    model = MockAlbumModel(
        id=uuid4(),
        title="Test Album",
        artist_id=uuid4(),
        artist_name="Test Artist",
        release_date=date(2020, 1, 1),
        total_tracks=10,
        play_count=5000,
        is_active=True,
    )

    # Mock de conversión a entidad
    def model_to_entity(model_instance):
        return AlbumEntity(
            id=str(model_instance.id),
            title=model_instance.title,
            artist_id=str(model_instance.artist_id),
            artist_name=model_instance.artist_name,
            release_date=model_instance.release_date,
            description=model_instance.description,
            cover_image_url=model_instance.cover_image_url,
            total_tracks=model_instance.total_tracks,
            play_count=model_instance.play_count,
            is_active=model_instance.is_active,
            created_at=model_instance.created_at,
            updated_at=model_instance.updated_at,
        )

    # Convertir a entidad
    entity = model_to_entity(model)

    # Verificaciones
    assert entity.title == model.title  # nosec B101
    assert entity.artist_name == model.artist_name  # nosec B101
    assert entity.total_tracks == model.total_tracks  # nosec B101
    assert entity.play_count == model.play_count  # nosec B101
    assert entity.is_active == model.is_active  # nosec B101

    print("✅ Conversión modelo a entidad funciona")
    print(f"   - Título: {entity.title}")
    print(f"   - Artista: {entity.artist_name}")
    print(f"   - Tipo entidad: {type(entity).__name__}")

    return True


def run_all_tests():
    """Ejecuta todos los tests de modelos Album"""
    print("🧪 TESTS DE MODELOS ALBUM")
    print("=" * 50)

    tests = [
        test_album_model_creation,
        test_album_model_minimal_data,
        test_album_model_string_representation,
        test_album_model_queries,
        test_album_model_updates,
        test_model_to_entity_conversion,
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
        print("🎉 ¡Todos los tests de modelos Album pasaron!")
        return True
    else:
        print(f"⚠️  {failed} tests fallaron")
        return False


if __name__ == "__main__":
    run_all_tests()
