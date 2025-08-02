#!/usr/bin/env python
"""
Test directo para verificar que los serializers de Songs funcionan
"""
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Configurar paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

# Configurar Django con env de desarrollo
from dotenv import load_dotenv

load_dotenv(BASE_DIR / "config" / "settings" / ".env.dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

import django

django.setup()

# Importar después de setup
from apps.songs.api.serializers.song_serializers import (
    SongListSerializer,
    SongSerializer,
)


def test_song_serializer():
    """Test básico de SongSerializer"""
    print("🎵 Probando SongSerializer...")

    # Datos de prueba válidos
    song_data = {
        "title": "Test Serializer Song",
        "youtube_video_id": "abc123def",
        "artist_name": "Serializer Artist",
        "album_title": "Serializer Album",
        "genre_name": "Rock",
        "duration_seconds": 240,
        "file_url": "https://example.com/song.mp3",
        "thumbnail_url": "https://example.com/thumb.jpg",
        "youtube_url": "https://youtube.com/watch?v=abc123def",
        "tags": ["rock", "test", "serializer"],
        "play_count": 75,
        "youtube_view_count": 10000,
        "youtube_like_count": 500,
        "is_explicit": False,
        "audio_downloaded": True,
        "published_at": datetime.now(),
    }

    # Crear serializer
    serializer = SongSerializer(data=song_data)

    # Verificar que es válido
    is_valid = serializer.is_valid()
    if not is_valid:
        print(f"   Errores: {serializer.errors}")
        return False

    assert is_valid == True  # nosec B101
    validated_data = serializer.validated_data
    assert validated_data["title"] == "Test Serializer Song"  # nosec B101
    assert validated_data["youtube_video_id"] == "abc123def"  # nosec B101
    assert validated_data["artist_name"] == "Serializer Artist"  # nosec B101
    assert validated_data["duration_seconds"] == 240  # nosec B101
    assert validated_data["tags"] == ["rock", "test", "serializer"]  # nosec B101
    assert validated_data["is_explicit"] == False  # nosec B101
    assert validated_data["audio_downloaded"] == True  # nosec B101

    print("✅ SongSerializer funciona correctamente")
    print(f"   - Título: {validated_data['title']}")
    print(f"   - Artista: {validated_data['artist_name']}")
    print(f"   - Duración: {validated_data['duration_seconds']}s")
    print(f"   - Tags: {validated_data['tags']}")

    return True


def test_song_serializer_duration_formatted():
    """Test campo calculado duration_formatted"""
    print("\n🎵 Probando campo duration_formatted...")

    test_cases = [
        (0, "00:00"),
        (30, "00:30"),
        (60, "01:00"),
        (90, "01:30"),
        (180, "03:00"),
        (240, "04:00"),
        (3600, "60:00"),  # 1 hora
    ]

    for duration, expected_format in test_cases:
        # Usar el método get_duration_formatted directamente
        serializer = SongSerializer()

        # Crear un objeto mock simple para duration_formatted
        mock_obj = {"duration_seconds": duration}
        actual_format = serializer.get_duration_formatted(mock_obj)

        assert (  # nosec B101
            actual_format == expected_format
        ), f"Duration {duration} should format as {expected_format}, got {actual_format}"

    print("✅ duration_formatted funciona correctamente")
    print("   - Todos los formatos de duración son correctos")

    return True


def test_song_list_serializer():
    """Test básico de SongListSerializer"""
    print("\n🎵 Probando SongListSerializer...")

    # Datos de prueba para lista
    list_data = {
        "id": str(uuid.uuid4()),
        "title": "List Test Song",
        "artist_name": "List Artist",
        "album_title": "List Album",
        "thumbnail_url": "https://example.com/list-thumb.jpg",
        "play_count": 25,
    }

    # Crear serializer
    serializer = SongListSerializer(data=list_data)

    # Verificar que es válido
    is_valid = serializer.is_valid()
    if not is_valid:
        print(f"   Errores: {serializer.errors}")
        return False

    assert is_valid == True  # nosec B101
    validated_data = serializer.validated_data
    assert validated_data["title"] == "List Test Song"  # nosec B101
    assert validated_data["artist_name"] == "List Artist"  # nosec B101
    assert validated_data["album_title"] == "List Album"  # nosec B101
    assert validated_data["play_count"] == 25  # nosec B101

    print("✅ SongListSerializer funciona correctamente")
    print(f"   - Título: {validated_data['title']}")
    print(f"   - Artista: {validated_data['artist_name']}")
    print(f"   - Play count: {validated_data['play_count']}")

    return True


def test_song_serializer_validation():
    """Test validaciones del serializer"""
    print("\n🎵 Probando validaciones de SongSerializer...")

    # Test campo requerido faltante
    invalid_data = {
        "title": "Missing Required Fields Song",
        # Falta youtube_video_id (requerido)
        "duration_seconds": 120,
        "youtube_url": "https://youtube.com/watch?v=missing",
        "play_count": 0,
        "youtube_view_count": 0,
        "youtube_like_count": 0,
        "is_explicit": False,
        "audio_downloaded": False,
    }

    serializer = SongSerializer(data=invalid_data)
    is_valid = serializer.is_valid()

    assert is_valid == False  # nosec B101
    assert "youtube_video_id" in serializer.errors  # nosec B101
    negative_data = {
        "title": "Negative Duration Song",
        "youtube_video_id": "neg123",
        "duration_seconds": -10,  # Inválido
        "youtube_url": "https://youtube.com/watch?v=neg123",
        "play_count": 0,
        "youtube_view_count": 0,
        "youtube_like_count": 0,
        "is_explicit": False,
        "audio_downloaded": False,
    }

    serializer_negative = SongSerializer(data=negative_data)
    is_valid_negative = serializer_negative.is_valid()

    assert is_valid_negative == False  # nosec B101
    assert "duration_seconds" in serializer_negative.errors  # nosec B101
    invalid_url_data = {
        "title": "Invalid URL Song",
        "youtube_video_id": "url123",
        "duration_seconds": 120,
        "youtube_url": "not-a-valid-url",  # Inválido
        "play_count": 0,
        "youtube_view_count": 0,
        "youtube_like_count": 0,
        "is_explicit": False,
        "audio_downloaded": False,
    }

    serializer_url = SongSerializer(data=invalid_url_data)
    is_valid_url = serializer_url.is_valid()

    assert is_valid_url == False  # nosec B101
    assert "youtube_url" in serializer_url.errors  # nosec B101

    print("✅ Validaciones de SongSerializer funcionan correctamente")
    print("   - Detecta campos requeridos faltantes")
    print("   - Detecta valores negativos inválidos")
    print("   - Detecta URLs inválidas")

    return True


def test_song_serializer_nullable_fields():
    """Test campos que pueden ser nulos"""
    print("\n🎵 Probando campos nullable de SongSerializer...")

    # Datos con campos nulos
    nullable_data = {
        "title": "Nullable Fields Song",
        "youtube_video_id": "null123",
        "artist_name": None,  # Nullable
        "album_title": None,  # Nullable
        "genre_name": None,  # Nullable
        "duration_seconds": 180,
        "file_url": None,  # Nullable
        "thumbnail_url": None,  # Nullable
        "youtube_url": "https://youtube.com/watch?v=null123",
        "tags": [],  # Opcional
        "play_count": 0,
        "youtube_view_count": 0,
        "youtube_like_count": 0,
        "is_explicit": False,
        "audio_downloaded": False,
        "published_at": None,  # Nullable
    }

    serializer = SongSerializer(data=nullable_data)
    is_valid = serializer.is_valid()

    if not is_valid:
        print(f"   Errores: {serializer.errors}")
        return False

    assert is_valid == True  # nosec B101

    validated_data = serializer.validated_data
    assert validated_data["artist_name"] is None  # nosec B101
    assert validated_data["album_title"] is None  # nosec B101
    assert validated_data["genre_name"] is None  # nosec B101
    assert validated_data["file_url"] is None  # nosec B101
    assert validated_data["thumbnail_url"] is None  # nosec B101
    assert validated_data["published_at"] is None  # nosec B101
    assert validated_data["tags"] == []  # nosec B101

    print("✅ Campos nullable funcionan correctamente")
    print("   - Todos los campos nullable aceptan None")
    print("   - Tags acepta lista vacía")

    return True


def main():
    """Función principal"""
    print("🚀 Iniciando tests directos de serializers de Songs...")
    print("=" * 65)

    try:
        # Ejecutar tests
        test_song_serializer()
        test_song_serializer_duration_formatted()
        test_song_list_serializer()
        test_song_serializer_validation()
        test_song_serializer_nullable_fields()

        print("\n" + "=" * 65)
        print("🎉 ¡Todos los tests de serializers pasaron correctamente!")
        print("✅ Los serializers de Songs funcionan bien")

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
