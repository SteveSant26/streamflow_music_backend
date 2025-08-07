#!/usr/bin/env python
"""
Test directo para verificar que los modelos de Songs funcionan
"""
import os
import sys
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

# Importar después de setup
from django.db import connection

from apps.songs.infrastructure.models.song_model import Song


def setup_test_database():
    """Configurar base de datos en memoria para tests"""
    # Crear tablas si no existen
    with connection.schema_editor() as schema_editor:
        if not connection.introspection.table_names():
            schema_editor.create_model(Song)


def test_song_model_creation():
    """Test básico de creación de modelo Song"""
    print("🎵 Probando creación de modelo Song...")

    # Datos de prueba
    song_data = {
        "title": "Test Song Model",
        "artist_name": "Model Test Artist",
        "album_title": "Model Test Album",
        "genre_name": "Rock",
        "duration_seconds": 200,
        "play_count": 150,
        "favorite_count": 25,
        "download_count": 10,
        "tags": ["rock", "test", "model"],
        "is_active": True,
        "is_explicit": False,
        "is_premium": False,
        "source_type": "youtube",
        "source_id": "test-youtube-123",
        "audio_quality": "standard",
    }

    # Crear modelo
    song = Song.objects.create(**song_data)

    # Verificaciones básicas
    assert song.id is not None  # nosec B101
    assert isinstance(song.id, uuid.UUID)  # nosec B101
    assert song.title == "Test Song Model"  # nosec B101
    assert song.artist_name == "Model Test Artist"  # nosec B101
    assert song.album_title == "Model Test Album"  # nosec B101
    assert song.genre_name == "Rock"  # nosec B101
    assert song.duration_seconds == 200  # nosec B101
    assert song.play_count == 150  # nosec B101
    assert song.tags == ["rock", "test", "model"]  # nosec B101
    assert song.is_active == True  # nosec B101
    assert song.is_explicit == False  # nosec B101
    assert song.source_type == "youtube"  # nosec B101
    assert song.created_at is not None  # nosec B101
    assert song.updated_at is not None  # nosec B101

    print("✅ Modelo Song creado correctamente")
    print(f"   - ID: {song.id}")
    print(f"   - Título: {song.title}")
    print(f"   - Artista: {song.artist_name}")
    print(f"   - Duración: {song.duration_seconds}s")
    print(f"   - Tags: {song.tags}")

    return song


def test_song_model_minimal():
    """Test con datos mínimos"""
    print("\n🎵 Probando modelo Song con datos mínimos...")

    song = Song.objects.create(title="Minimal Model Song")

    # Verificaciones
    assert song.title == "Minimal Model Song"  # nosec B101
    assert song.duration_seconds == 0  # nosec B101
    assert song.play_count == 0  # nosec B101
    assert song.favorite_count == 0  # nosec B101
    assert song.download_count == 0  # nosec B101
    assert song.tags == []  # nosec B101
    assert song.is_active == True  # nosec B101
    assert song.is_explicit == False  # nosec B101
    assert song.is_premium == False  # nosec B101
    assert song.source_type == "youtube"  # nosec B101
    assert song.audio_quality == "standard"  # nosec B101

    print("✅ Modelo Song mínimo creado correctamente")

    return song


def test_song_model_queries():
    """Test consultas básicas del modelo"""
    print("\n🎵 Probando consultas del modelo Song...")

    # Crear algunas canciones de prueba
    songs_data = [
        {"title": "Rock Song 1", "genre_name": "Rock", "play_count": 100},
        {"title": "Pop Song 1", "genre_name": "Pop", "play_count": 200},
        {"title": "Rock Song 2", "genre_name": "Rock", "play_count": 150},
    ]

    created_songs = []
    for data in songs_data:
        song = Song.objects.create(**data)
        created_songs.append(song)

    # Test filtrado por género
    rock_songs = Song.objects.filter(genre_name="Rock")
<<<<<<< HEAD
    assert rock_songs.count() >= 2  # nosec B101

    pop_songs = Song.objects.filter(genre_name="Pop")
    assert pop_songs.count() >= 1  # nosec B101

    # Test ordenamiento por play_count
    popular_songs = Song.objects.order_by("-play_count")
    assert popular_songs.count() >= 3  # nosec B101
    rock_title_songs = Song.objects.filter(title__icontains="Rock")
    assert rock_title_songs.count() >= 2  # nosec B101
    active_songs = Song.objects.filter(is_active=True)
    assert active_songs.count() >= 3  # nosec B101
=======
    assert rock_songs.count( >= 2)  # nosec B101

    pop_songs = Song.objects.filter(genre_name="Pop")
    assert pop_songs.count( >= 1)  # nosec B101

    # Test ordenamiento por play_count
    popular_songs = Song.objects.order_by("-play_count")
    assert popular_songs.count( >= 3)  # nosec B101
    rock_title_songs = Song.objects.filter(title__icontains="Rock")
    assert rock_title_songs.count( >= 2)  # nosec B101
    active_songs = Song.objects.filter(is_active=True)
    assert active_songs.count( >= 3)  # nosec B101
>>>>>>> 6ade253d2d17092a2431a2a5ec5d0496c0943e33

    print("✅ Consultas del modelo Song funcionan correctamente")
    print(f"   - Canciones Rock: {rock_songs.count()}")
    print(f"   - Canciones Pop: {pop_songs.count()}")
    print(f"   - Canciones activas: {active_songs.count()}")

    return True


def test_song_model_updates():
    """Test actualización de modelos"""
    print("\n🎵 Probando actualización de modelo Song...")

    # Crear canción
    song = Song.objects.create(title="Updatable Song", play_count=50)

    original_updated_at = song.updated_at

    # Actualizar
    song.title = "Updated Song Title"
    song.play_count = 100
    song.save()

    # Recargar de BD
    song.refresh_from_db()

    # Verificaciones
    assert song.title == "Updated Song Title"  # nosec B101
    assert song.play_count == 100  # nosec B101
    assert song.updated_at > original_updated_at  # nosec B101

    print("✅ Actualización de modelo Song funciona correctamente")
    print(f"   - Nuevo título: {song.title}")
    print(f"   - Nuevo play_count: {song.play_count}")

    return True


def main():
    """Función principal"""
    print("🚀 Iniciando tests directos de modelos de Songs...")
    print("=" * 60)

    try:
        # Configurar BD de test
        setup_test_database()

        # Ejecutar tests
        test_song_model_creation()
        test_song_model_minimal()
        test_song_model_queries()
        test_song_model_updates()

        print("\n" + "=" * 60)
        print("🎉 ¡Todos los tests de modelos pasaron correctamente!")
        print("✅ Los modelos de Songs funcionan bien")

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
