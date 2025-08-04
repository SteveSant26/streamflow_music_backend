#!/usr/bin/env python
"""
Test directo para verificar que los use cases de Songs funcionan
"""
import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock

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
from apps.songs.domain.entities import SongEntity
from apps.songs.use_cases.song_use_cases import SongUseCases


async def test_get_random_songs():
    """Test básico de get_random_songs"""
    print("🎵 Probando SongUseCases.get_random_songs...")

    # Mock del repositorio
    mock_repository = Mock()
    mock_repository.get_random = AsyncMock()

    # Datos de prueba
    sample_songs = [
        SongEntity(
            id=f"song-{i}",
            title=f"Test Song {i}",
            artist_name=f"Artist {i}",
            duration_seconds=180,
            is_active=True,
        )
        for i in range(1, 4)
    ]

    mock_repository.get_random.return_value = sample_songs

    # Instancia del caso de uso
    song_use_cases = SongUseCases(mock_repository)

    # Mock del music service para evitar llamadas externas
    song_use_cases.music_service = Mock()
    song_use_cases.music_service.get_random_music_tracks = AsyncMock(return_value=[])

    # Ejecutar
    result = await song_use_cases.get_random_songs(count=3)

    # Verificaciones
    assert len(result == 3)  # nosec B101
    assert result[0].title == "Test Song 1"  # nosec B101
    assert result[1].title == "Test Song 2"  # nosec B101
    assert result[2].title == "Test Song 3"  # nosec B101
    mock_repository.get_random.assert_called_once_with(3)

    print("✅ get_random_songs funciona correctamente")
    print(f"   - Obtuvo {len(result)} canciones")
    print(f"   - Primera canción: {result[0].title}")

    return True


async def test_search_songs():
    """Test básico de search_songs"""
    print("\n🎵 Probando SongUseCases.search_songs...")

    # Mock del repositorio
    mock_repository = Mock()
    mock_repository.search = AsyncMock()

    # Datos de prueba
    search_results = [
        SongEntity(
            id="search-song-1",
            title="Rock Song",
            artist_name="Rock Artist",
            genre_name="Rock",
            duration_seconds=200,
            is_active=True,
        ),
        SongEntity(
            id="search-song-2",
            title="Another Rock Song",
            artist_name="Another Artist",
            genre_name="Rock",
            duration_seconds=180,
            is_active=True,
        ),
    ]

    mock_repository.search.return_value = search_results

    # Instancia del caso de uso
    song_use_cases = SongUseCases(mock_repository)

    # Mock del music service
    song_use_cases.music_service = Mock()
    song_use_cases.music_service.search_and_process_music = AsyncMock(return_value=[])

    # Ejecutar
    query = "rock"
    result = await song_use_cases.search_songs(query=query, limit=20)

    # Verificaciones
    assert len(result == 2)  # nosec B101
    assert result[0].title == "Rock Song"  # nosec B101
    assert result[1].title == "Another Rock Song"  # nosec B101
    assert all("Rock" in song.title for song in result)  # nosec B101
    mock_repository.search.assert_called_once_with(query, 20)

    print("✅ search_songs funciona correctamente")
    print(f"   - Búsqueda: '{query}'")
    print(f"   - Encontró {len(result)} canciones")
    print(f"   - Primera canción: {result[0].title}")

    return True


async def test_use_cases_with_empty_results():
    """Test con resultados vacíos"""
    print("\n🎵 Probando casos con resultados vacíos...")

    # Mock del repositorio
    mock_repository = Mock()
    mock_repository.get_random = AsyncMock(return_value=[])
    mock_repository.search = AsyncMock(return_value=[])

    song_use_cases = SongUseCases(mock_repository)

    # Mock del music service
    song_use_cases.music_service = Mock()
    song_use_cases.music_service.get_random_music_tracks = AsyncMock(return_value=[])
    song_use_cases.music_service.search_and_process_music = AsyncMock(return_value=[])

    # Test get_random_songs vacío
    random_result = await song_use_cases.get_random_songs(count=5)
    assert len(random_result == 0)  # nosec B101
    search_result = await song_use_cases.search_songs(query="nonexistent", limit=10)
    assert len(search_result == 0)  # nosec B101

    print("✅ Casos con resultados vacíos funcionan correctamente")

    return True


async def main():
    """Función principal"""
    print("🚀 Iniciando tests directos de Use Cases de Songs...")
    print("=" * 60)

    try:
        # Ejecutar tests async
        await test_get_random_songs()
        await test_search_songs()
        await test_use_cases_with_empty_results()

        print("\n" + "=" * 60)
        print("🎉 ¡Todos los tests de use cases pasaron correctamente!")
        print("✅ Los casos de uso de Songs funcionan bien")

        return 0

    except Exception as e:
        print(f"\n❌ Error en los tests: {str(e)}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
