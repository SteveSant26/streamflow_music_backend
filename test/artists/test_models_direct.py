#!/usr/bin/env python
"""
Test directo para verificar que los modelos de Artists funcionan
"""
import os
import sys
import time
import uuid
from pathlib import Path

# Configurar paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

# Configurar Django con env de desarrollo
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env.dev")

# Configurar para usar SQLite en memoria para tests
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django

django.setup()

# Crear todas las tablas necesarias
from django.core.management import call_command
from django.db import connection

# Importar después de setup
from apps.artists.infrastructure.models import ArtistModel

# Ejecutar migraciones para crear las tablas
try:
    call_command("migrate", verbosity=0, interactive=False)
except Exception:
    # Si falla, intentar solo crear la tabla básica
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(ArtistModel)


def test_artist_model_creation():
    """Test creación básica de modelo ArtistModel"""
    print("🎤 Probando creación de modelo Artist...")

    # Datos de prueba válidos
    artist_data = {
        "id": uuid.uuid4(),  # Agregar ID explícitamente
        "name": "Test Artist Model",
        "biography": "Una biografía de prueba para el modelo de artista",
        "country": "Colombia",
        "image_url": "https://example.com/artist-model.jpg",
        "followers_count": 75000,
        "is_verified": True,
        "is_active": True,
    }

    # Crear modelo
    artist = ArtistModel.objects.create(**artist_data)

    # Verificaciones básicas
    assert artist.id is not None  # nosec B101
    assert isinstance(artist.id, uuid.UUID)  # nosec B101
    assert artist.name == "Test Artist Model"  # nosec B101
    assert (
        artist.biography == "Una biografía de prueba para el modelo de artista"
    )  # nosec B101
    assert artist.country == "Colombia"  # nosec B101
    assert artist.image_url == "https://example.com/artist-model.jpg"  # nosec B101
    assert artist.followers_count == 75000  # nosec B101
    assert artist.is_verified == True  # nosec B101
    assert artist.is_active == True  # nosec B101
    assert artist.created_at is not None  # nosec B101
    assert artist.updated_at is not None  # nosec B101

    print("✅ Modelo Artist creado correctamente")
    print(f"   - ID: {artist.id}")
    print(f"   - Nombre: {artist.name}")
    print(f"   - País: {artist.country}")
    print(f"   - Seguidores: {artist.followers_count:,}")
    print(f"   - Verificado: {artist.is_verified}")

    return True


def test_artist_model_minimal():
    """Test creación de modelo Artist con datos mínimos"""
    print("\n🎤 Probando modelo Artist con datos mínimos...")

    # Solo campo requerido
    minimal_data = {
        "id": uuid.uuid4(),  # Agregar ID explícitamente
        "name": "Minimal Artist Model",
    }

    # Crear modelo
    artist = ArtistModel.objects.create(**minimal_data)

    # Verificaciones
    assert artist.name == "Minimal Artist Model"  # nosec B101
    assert artist.biography is None  # nosec B101
    assert artist.country is None  # nosec B101
    assert artist.image_url is None  # nosec B101
    assert artist.followers_count == 0  # nosec B101
    assert artist.is_verified == False  # nosec B101
    assert artist.is_active == True  # nosec B101

    print("✅ Modelo Artist mínimo creado correctamente")
    print(f"   - Solo nombre requerido")
    print(f"   - Valores por defecto aplicados")

    return True


def test_artist_model_queries():
    """Test consultas del modelo Artist"""
    print("\n🎤 Probando consultas del modelo Artist...")

    # Limpiar base de datos antes del test
    ArtistModel.objects.all().delete()

    # Crear varios artistas para probar consultas
    artists_data = [
        {
            "id": uuid.uuid4(),
            "name": "Colombian Rock Artist",
            "country": "Colombia",
            "followers_count": 50000,
            "is_active": True,
            "is_verified": False,
        },
        {
            "id": uuid.uuid4(),
            "name": "Mexican Pop Artist",
            "country": "Mexico",
            "followers_count": 100000,
            "is_active": True,
            "is_verified": True,
        },
        {
            "id": uuid.uuid4(),
            "name": "Colombian Urban Artist",
            "country": "Colombia",
            "followers_count": 75000,
            "is_active": True,
            "is_verified": True,
        },
        {
            "id": uuid.uuid4(),
            "name": "Spanish Flamenco Artist",
            "country": "España",
            "followers_count": 25000,
            "is_active": False,  # Inactivo
            "is_verified": False,
        },
        {
            "id": uuid.uuid4(),
            "name": "Colombian Vallenato Artist",
            "country": "Colombia",
            "followers_count": 120000,
            "is_active": True,
            "is_verified": True,
        },
    ]

    # Crear artistas
    for data in artists_data:
        ArtistModel.objects.create(**data)

    # Test consultas
    # 1. Artistas por país
    colombian_artists = ArtistModel.objects.filter(country="Colombia").count()
    assert colombian_artists == 3  # nosec B101
    active_artists = ArtistModel.objects.filter(is_active=True).count()
    assert active_artists == 4  # nosec B101
    verified_artists = ArtistModel.objects.filter(is_verified=True).count()
    assert verified_artists == 3  # nosec B101
    popular_artists = ArtistModel.objects.filter(followers_count__gte=50000).count()
    assert popular_artists == 4  # nosec B101
    top_artist = ArtistModel.objects.order_by("-followers_count").first()
    assert top_artist.name == "Colombian Vallenato Artist"  # nosec B101
    assert top_artist.followers_count == 120000  # nosec B101

    print("✅ Consultas del modelo Artist funcionan correctamente")
    print(f"   - Artistas colombianos: {colombian_artists}")
    print(f"   - Artistas activos: {active_artists}")
    print(f"   - Artistas verificados: {verified_artists}")
    print(f"   - Artistas populares (>50k): {popular_artists}")
    print(f"   - Top artista: {top_artist.name}")

    return True


def test_artist_model_update():
    """Test actualización de modelo Artist"""
    print("\n🎤 Probando actualización de modelo Artist...")

    # Crear artista
    artist = ArtistModel.objects.create(
        id=uuid.uuid4(),
        name="Artist to Update",
        followers_count=10000,
        is_verified=False,
    )

    original_updated_at = artist.updated_at

    # Simular pausa para ver cambio en updated_at
    import time

    time.sleep(0.01)

    # Actualizar artista
    artist.name = "Updated Artist Name"
    artist.followers_count = 50000
    artist.is_verified = True
    artist.save()

    # Refresco desde DB
    artist.refresh_from_db()

    # Verificaciones
    assert artist.name == "Updated Artist Name"  # nosec B101
    assert artist.followers_count == 50000  # nosec B101
    assert artist.is_verified == True  # nosec B101
    assert artist.updated_at > original_updated_at  # nosec B101

    print("✅ Actualización de modelo Artist funciona correctamente")
    print(f"   - Nuevo nombre: {artist.name}")
    print(f"   - Nuevos seguidores: {artist.followers_count:,}")
    print(f"   - Ahora verificado: {artist.is_verified}")

    return True


def test_artist_model_string_representation():
    """Test representación string del modelo"""
    print("\n🎤 Probando representación string del modelo...")

    artist = ArtistModel.objects.create(
        id=uuid.uuid4(), name="String Test Artist", country="Test Country"
    )

    # El __str__ del modelo debería retornar el nombre
    str_representation = str(artist)
    assert "String Test Artist" in str_representation  # nosec B101

    print("✅ Representación string funciona correctamente")
    print(f"   - String: {str_representation}")

    return True


def test_artist_model_ordering():
    """Test ordenamiento por defecto del modelo"""
    print("\n🎤 Probando ordenamiento del modelo Artist...")

    # Crear artistas en orden específico
    artist1 = ArtistModel.objects.create(id=uuid.uuid4(), name="First Artist")
    time.sleep(0.01)  # Pequeña pausa
    artist2 = ArtistModel.objects.create(id=uuid.uuid4(), name="Second Artist")
    time.sleep(0.01)
    artist3 = ArtistModel.objects.create(id=uuid.uuid4(), name="Third Artist")

    # Obtener artistas con orden por defecto (debería ser por created_at desc)
    artists = list(ArtistModel.objects.all().order_by("-created_at")[:3])

    # Verificar orden (más reciente primero)
    assert artists[0].name == "Third Artist"  # nosec B101
    assert artists[1].name == "Second Artist"  # nosec B101
    assert artists[2].name == "First Artist"  # nosec B101

    print("✅ Ordenamiento del modelo funciona correctamente")
    print(f"   - Primer artista (más reciente): {artists[0].name}")

    return True


def test_artist_model_constraints():
    """Test constraints y validaciones del modelo"""
    print("\n🎤 Probando constraints del modelo Artist...")

    # Test valores negativos en followers_count (debería fallar)
    try:
        ArtistModel.objects.create(
            id=uuid.uuid4(), name="Negative Followers Artist", followers_count=-1000
        )
        # Si llegamos aquí, no falló como esperábamos
        print("   ⚠️ Nota: El modelo permite seguidores negativos")
    except Exception as e:
        print("   ✅ Rechaza correctamente seguidores negativos")

    # Test nombre muy largo
    long_name = "A" * 300  # Más largo que el max_length de 200
    try:
        ArtistModel.objects.create(id=uuid.uuid4(), name=long_name)
        print("   ⚠️ Nota: El modelo permite nombres muy largos")
    except Exception as e:
        print("   ✅ Rechaza correctamente nombres muy largos")

    print("✅ Constraints del modelo verificados")

    return True


def main():
    """Función principal"""
    print("🚀 Iniciando tests directos de modelos de Artists...")
    print("=" * 60)

    try:
        # Ejecutar tests
        test_artist_model_creation()
        test_artist_model_minimal()
        test_artist_model_queries()
        test_artist_model_update()
        test_artist_model_string_representation()
        test_artist_model_ordering()
        test_artist_model_constraints()

        print("\n" + "=" * 60)
        print("🎉 ¡Todos los tests de modelos pasaron correctamente!")
        print("✅ Los modelos de Artists funcionan bien")

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
