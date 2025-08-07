#!/usr/bin/env python3
"""
Tests para modelos de Genre (Infrastructure)
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

    print("✅ Entidades importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando: {e}")
    sys.exit(1)


# Mock del modelo Django para evitar dependencias
class MockGenreModel:
    """Mock del GenreModel de Django"""

    _instances = []  # Simular base de datos en memoria

    def __init__(self, **kwargs):
        self.id = kwargs.get("id", str(uuid4()))
        self.name = kwargs.get("name", "")
        self.description = kwargs.get("description", None)
        self.image_url = kwargs.get("image_url", None)
        self.color_hex = kwargs.get("color_hex", None)
        self.popularity_score = kwargs.get("popularity_score", 0)
        self.is_active = kwargs.get("is_active", True)
        self.created_at = kwargs.get("created_at", datetime.now())
        self.updated_at = kwargs.get("updated_at", datetime.now())

    def __str__(self):
        return self.name

    def save(self):
        """Simular guardado"""
        self.updated_at = datetime.now()
        if self not in MockGenreModel._instances:
            MockGenreModel._instances.append(self)

    @classmethod
    def objects_all(cls):
        """Simular queryset.all()"""
        return cls._instances.copy()

    @classmethod
    def objects_filter(cls, **kwargs):
        """Simular queryset.filter()"""
        results = []
        for instance in cls._instances:
            match = True
            for key, value in kwargs.items():
                if not hasattr(instance, key) or getattr(instance, key) != value:
                    match = False
                    break
            if match:
                results.append(instance)
        return results

    @classmethod
    def objects_get(cls, **kwargs):
        """Simular queryset.get()"""
        results = cls.objects_filter(**kwargs)
        if len(results) == 0:
            raise Exception("DoesNotExist")
        elif len(results) > 1:
            raise Exception("MultipleObjectsReturned")
        return results[0]

    @classmethod
    def clear_instances(cls):
        """Limpiar instancias para tests"""
        cls._instances.clear()

    def to_entity(self):
        """Convertir modelo a entidad del dominio"""
        return GenreEntity(
            id=str(self.id),
            name=self.name,
            description=self.description,
            image_url=self.image_url,
            color_hex=self.color_hex,
            popularity_score=self.popularity_score,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )


def test_genre_model_creation():
    """Test creación del modelo GenreModel"""
    print("🎼 Probando creación de MockGenreModel...")

    # Limpiar instancias previas
    MockGenreModel.clear_instances()

    # Crear modelo con datos completos
    genre_data = {
        "id": str(uuid4()),
        "name": "Rock",
        "description": "Rock music genre",
        "image_url": "https://example.com/rock.jpg",
        "color_hex": "#FF6B35",
        "popularity_score": 85,
        "is_active": True,
    }

    genre_model = MockGenreModel(**genre_data)
    genre_model.save()

    # Verificaciones
    assert genre_model.id == genre_data["id"]  # nosec B101
    assert genre_model.name == "Rock"  # nosec B101
    assert genre_model.description == "Rock music genre"  # nosec B101
    assert genre_model.image_url == "https://example.com/rock.jpg"  # nosec B101
    assert genre_model.color_hex == "#FF6B35"  # nosec B101
    assert genre_model.popularity_score == 85  # nosec B101
    assert genre_model.is_active == True  # nosec B101
    assert genre_model.created_at is not None  # nosec B101
    assert genre_model.updated_at is not None  # nosec B101

    print("✅ MockGenreModel se crea correctamente")
    print(f"   - Nombre: {genre_model.name}")
    print(f"   - Descripción: {genre_model.description}")
    print(f"   - Popularidad: {genre_model.popularity_score}")


def test_genre_model_minimal_data():
    """Test creación del modelo con datos mínimos"""
    print("🎼 Probando MockGenreModel con datos mínimos...")

    # Limpiar instancias previas
    MockGenreModel.clear_instances()

    # Crear modelo con datos mínimos
    minimal_genre = MockGenreModel(name="Jazz")
    minimal_genre.save()

    # Verificaciones
    assert minimal_genre.name == "Jazz"  # nosec B101
    assert minimal_genre.description is None  # nosec B101
    assert minimal_genre.image_url is None  # nosec B101
    assert minimal_genre.color_hex is None  # nosec B101
    assert minimal_genre.popularity_score == 0  # nosec B101
    assert minimal_genre.is_active == True  # nosec B101
    assert minimal_genre.created_at is not None  # nosec B101
    assert minimal_genre.updated_at is not None  # nosec B101

    print("✅ MockGenreModel se crea correctamente con datos mínimos")
    print(f"   - Nombre: {minimal_genre.name}")
    print(f"   - Activo por defecto: {minimal_genre.is_active}")


def test_genre_model_string_representation():
    """Test representación string del modelo"""
    print("🎼 Probando representación string del modelo...")

    genre = MockGenreModel(name="Electronic")
    genre_str = str(genre)

    assert genre_str == "Electronic"  # nosec B101

    print("✅ Representación string funciona correctamente")
    print(f"   - String: {genre_str}")


def test_genre_model_queries():
    """Test consultas del modelo"""
    print("🎼 Probando consultas del modelo...")

    # Limpiar y crear datos de prueba
    MockGenreModel.clear_instances()

    # Crear varios géneros
    genres_data = [
        {"name": "Rock", "is_active": True, "popularity_score": 85},
        {"name": "Pop", "is_active": True, "popularity_score": 95},
        {"name": "Jazz", "is_active": False, "popularity_score": 70},
    ]

    for data in genres_data:
        genre = MockGenreModel(**data)
        genre.save()

    # Test queries
    all_genres = MockGenreModel.objects_all()
    active_genres = MockGenreModel.objects_filter(is_active=True)
    inactive_genres = MockGenreModel.objects_filter(is_active=False)

    # Verificaciones
    assert len(all_genres == 3)  # nosec B101
    assert len(active_genres == 2)  # nosec B101
    assert len(inactive_genres == 1)  # nosec B101
    rock_genre = MockGenreModel.objects_get(name="Rock")
    assert rock_genre.name == "Rock"  # nosec B101
    assert rock_genre.popularity_score == 85  # nosec B101

    print("✅ Consultas del modelo funcionan correctamente")
    print(f"   - Total géneros: {len(all_genres)}")
    print(f"   - Géneros activos: {len(active_genres)}")
    print(f"   - Géneros inactivos: {len(inactive_genres)}")


def test_genre_model_updates():
    """Test actualizaciones del modelo"""
    print("🎼 Probando actualizaciones del modelo...")

    # Limpiar y crear género
    MockGenreModel.clear_instances()

    genre = MockGenreModel(name="Classical", popularity_score=60)
    original_updated_at = genre.updated_at
    genre.save()

    # Simular pequeña pausa para diferente timestamp
    import time

    time.sleep(0.01)

    # Actualizar modelo
    genre.name = "Classical Music"
    genre.popularity_score = 75
    genre.save()

    # Verificaciones
    assert genre.name == "Classical Music"  # nosec B101
    assert genre.popularity_score == 75  # nosec B101
    assert genre.updated_at > original_updated_at  # nosec B101

    print("✅ Actualizaciones del modelo funcionan correctamente")
    print(f"   - Nombre actualizado: {genre.name}")
    print(f"   - Popularidad actualizada: {genre.popularity_score}")


def test_model_to_entity_conversion():
    """Test conversión de modelo a entidad"""
    print("🎼 Probando conversión modelo a entidad...")

    # Crear modelo
    genre_model = MockGenreModel(
        name="Test Genre",
        description="Test description",
        color_hex="#FF0000",
        popularity_score=80,
    )

    # Convertir a entidad
    genre_entity = genre_model.to_entity()

    # Verificaciones
    assert isinstance(genre_entity, GenreEntity)  # nosec B101
    assert genre_entity.name == "Test Genre"  # nosec B101
    assert genre_entity.description == "Test description"  # nosec B101
<<<<<<< HEAD
    assert genre_entity.color_hex == "#FF0000"  # nosec B101
=======
    assert genre_entity.color_hex == "  # nosec B101
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33
    assert genre_entity.popularity_score == 80  # nosec B101
    assert genre_entity.is_active == True  # nosec B101

    print("✅ Conversión modelo a entidad funciona")
    print(f"   - Nombre: {genre_entity.name}")
    print(f"   - Descripción: {genre_entity.description}")
    print(f"   - Tipo entidad: {type(genre_entity).__name__}")


def test_model_edge_cases():
    """Test casos extremos del modelo"""
    print("🎼 Probando casos extremos...")

    # Limpiar instancias
    MockGenreModel.clear_instances()

    # Test con valores límite
    edge_genre = MockGenreModel(
        name="Edge Case Genre",
        popularity_score=100,  # Máximo
        color_hex="#000000",  # Negro
    )
    edge_genre.save()

    assert edge_genre.popularity_score == 100  # nosec B101
<<<<<<< HEAD
    assert edge_genre.color_hex == "#FF0000"  # nosec B101
=======
    assert edge_genre.color_hex == "  # nosec B101
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

    # Test búsqueda que no existe
    try:
        MockGenreModel.objects_get(name="Nonexistent Genre")
        assert False, "Debería haber lanzado excepción"  # nosec B101
    except Exception as e:
        assert "DoesNotExist" in str(e)  # nosec B101

    print("✅ Casos extremos funcionan correctamente")


def run_all_tests():
    """Ejecutar todos los tests de modelos Genre"""
    print("🧪 TESTS DE MODELOS GENRE")
    print("=" * 50)

    tests = [
        test_genre_model_creation,
        test_genre_model_minimal_data,
        test_genre_model_string_representation,
        test_genre_model_queries,
        test_genre_model_updates,
        test_model_to_entity_conversion,
        test_model_edge_cases,
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
        print("🎉 ¡Todos los tests de modelos Genre pasaron!")
    else:
        print("⚠️ Algunos tests fallaron")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
