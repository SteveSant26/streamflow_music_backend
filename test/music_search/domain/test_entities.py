#!/usr/bin/env python3
"""
Tests para entidades del dominio Music Search
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
    from src.apps.music_search.domain.entities import (
        SearchQueryEntity,
        SearchResponseEntity,
        SearchResultEntity,
    )
    from src.apps.music_search.domain.interfaces import MusicTrackData, YouTubeVideoInfo

    print("✅ Entidades MusicSearch importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando entidades MusicSearch: {e}")
    sys.exit(1)


def test_search_result_entity_creation():
    """Test creación de entidad SearchResultEntity"""
    print("🔍 Probando creación de SearchResultEntity...")

    # Datos completos
    result_data = {
        "result_type": "song",
        "result_id": "song-123",
        "title": "Bohemian Rhapsody",
        "subtitle": "Queen",
        "image_url": "https://example.com/queen.jpg",
        "relevance_score": 0.95,
    }

    # Crear entidad
    result = SearchResultEntity(**result_data)

    # Verificaciones
    assert result.result_type == "song"
    assert result.result_id == "song-123"
    assert result.title == "Bohemian Rhapsody"
    assert result.subtitle == "Queen"
    assert result.image_url == "https://example.com/queen.jpg"
    assert result.relevance_score == 0.95

    print("✅ SearchResultEntity se crea correctamente con datos completos")
    print(f"   - Tipo: {result.result_type}")
    print(f"   - Título: {result.title}")
    print(f"   - Artista: {result.subtitle}")
    print(f"   - Relevancia: {result.relevance_score}")


def test_search_result_entity_minimal_data():
    """Test creación de SearchResultEntity con datos mínimos"""
    print("🔍 Probando SearchResultEntity con datos mínimos...")

    # Datos mínimos requeridos
    minimal_data = {
        "result_type": "artist",
        "result_id": "artist-456",
        "title": "The Beatles",
    }

    # Crear entidad
    result = SearchResultEntity(**minimal_data)

    # Verificaciones
    assert result.result_type == "artist"
    assert result.result_id == "artist-456"
    assert result.title == "The Beatles"

    # Valores por defecto
    assert result.subtitle is None
    assert result.image_url is None
    assert result.relevance_score == 0.0

    print("✅ SearchResultEntity se crea correctamente con datos mínimos")
    print(f"   - Tipo: {result.result_type}")
    print(f"   - Título: {result.title}")
    print(f"   - ID: {result.result_id}")


def test_search_query_entity_creation():
    """Test creación de entidad SearchQueryEntity"""
    print("🔍 Probando creación de SearchQueryEntity...")

    # Datos completos
    query_data = {
        "id": str(uuid4()),
        "query_text": "rock music",
        "user_id": "user-123",
        "filters": {"genre": "rock", "year": "2020"},
        "results_count": 25,
        "created_at": datetime.now(),
    }

    # Crear entidad
    query = SearchQueryEntity(**query_data)

    # Verificaciones
    assert query.id == query_data["id"]
    assert query.query_text == "rock music"
    assert query.user_id == "user-123"
    assert query.filters == {"genre": "rock", "year": "2020"}
    assert query.results_count == 25
    assert query.created_at is not None

    print("✅ SearchQueryEntity se crea correctamente")
    print(f"   - Query: {query.query_text}")
    print(f"   - Usuario: {query.user_id}")
    print(f"   - Filtros: {query.filters}")
    print(f"   - Resultados: {query.results_count}")


def test_search_response_entity_creation():
    """Test creación de entidad SearchResponseEntity"""
    print("🔍 Probando creación de SearchResponseEntity...")

    # Crear resultados de muestra
    artists = [
        SearchResultEntity("artist", "a1", "Queen", relevance_score=0.9),
        SearchResultEntity("artist", "a2", "The Beatles", relevance_score=0.85),
    ]

    albums = [
        SearchResultEntity(
            "album", "al1", "Abbey Road", "The Beatles", relevance_score=0.8
        )
    ]

    songs = [
        SearchResultEntity(
            "song", "s1", "Bohemian Rhapsody", "Queen", relevance_score=0.95
        ),
        SearchResultEntity(
            "song", "s2", "Come Together", "The Beatles", relevance_score=0.88
        ),
    ]

    genres = [SearchResultEntity("genre", "g1", "Rock", relevance_score=0.75)]

    # Crear respuesta
    response = SearchResponseEntity(
        query="rock music",
        artists=artists,
        albums=albums,
        songs=songs,
        genres=genres,
        total_results=6,
        search_time_ms=125.5,
    )

    # Verificaciones
    assert response.query == "rock music"
    assert len(response.artists) == 2
    assert len(response.albums) == 1
    assert len(response.songs) == 2
    assert len(response.genres) == 1
    assert response.total_results == 6
    assert response.search_time_ms == 125.5

    print("✅ SearchResponseEntity se crea correctamente")
    print(f"   - Query: {response.query}")
    print(f"   - Artistas: {len(response.artists)}")
    print(f"   - Álbumes: {len(response.albums)}")
    print(f"   - Canciones: {len(response.songs)}")
    print(f"   - Total: {response.total_results}")
    print(f"   - Tiempo: {response.search_time_ms}ms")


def test_youtube_video_info_creation():
    """Test creación de entidad YouTubeVideoInfo"""
    print("🔍 Probando creación de YouTubeVideoInfo...")

    # Datos completos
    video_data = {
        "video_id": "dQw4w9WgXcQ",
        "title": "Never Gonna Give You Up",
        "channel_title": "Rick Astley",
        "channel_id": "UC-lHJZR3Gqxm24_Vd_AJ5Yw",
        "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "description": "Official video for Never Gonna Give You Up",
        "duration_seconds": 213,
        "published_at": datetime(2009, 10, 25),
        "view_count": 1000000000,
        "like_count": 10000000,
        "tags": ["rick astley", "pop", "80s"],
        "category_id": "10",
        "genre": "Pop",
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    }

    # Crear entidad
    video = YouTubeVideoInfo(**video_data)

    # Verificaciones
    assert video.video_id == "dQw4w9WgXcQ"
    assert video.title == "Never Gonna Give You Up"
    assert video.channel_title == "Rick Astley"
    assert video.duration_seconds == 213
    assert video.view_count == 1000000000
    assert video.genre == "Pop"
    assert len(video.tags) == 3

    print("✅ YouTubeVideoInfo se crea correctamente")
    print(f"   - Título: {video.title}")
    print(f"   - Canal: {video.channel_title}")
    print(f"   - Duración: {video.duration_seconds}s")
    print(f"   - Vistas: {video.view_count:,}")


def test_music_track_data_creation():
    """Test creación de entidad MusicTrackData"""
    print("🔍 Probando creación de MusicTrackData...")

    # Datos completos
    track_data = {
        "video_id": "dQw4w9WgXcQ",
        "title": "Never Gonna Give You Up",
        "artist_name": "Rick Astley",
        "album_title": "Whenever You Need Somebody",
        "duration_seconds": 213,
        "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        "genre": "Pop",
        "tags": ["rick astley", "pop", "80s"],
        "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "audio_file_data": b"mock_audio_data",
    }

    # Crear entidad
    track = MusicTrackData(**track_data)

    # Verificaciones
    assert track.video_id == "dQw4w9WgXcQ"
    assert track.title == "Never Gonna Give You Up"
    assert track.artist_name == "Rick Astley"
    assert track.album_title == "Whenever You Need Somebody"
    assert track.duration_seconds == 213
    assert track.genre == "Pop"
    assert len(track.tags) == 3
    assert track.audio_file_data == b"mock_audio_data"

    print("✅ MusicTrackData se crea correctamente")
    print(f"   - Título: {track.title}")
    print(f"   - Artista: {track.artist_name}")
    print(f"   - Álbum: {track.album_title}")
    print(f"   - Género: {track.genre}")


def test_entity_string_representations():
    """Test representaciones string de las entidades"""
    print("🔍 Probando representaciones string...")

    # SearchResultEntity
    result = SearchResultEntity("song", "id-1", "Test Song", "Test Artist")
    result_str = str(result)
    assert "SearchResultEntity" in result_str
    assert "Test Song" in result_str

    # SearchQueryEntity
    query = SearchQueryEntity("q-1", "test query")
    query_str = str(query)
    assert "SearchQueryEntity" in query_str
    assert "test query" in query_str

    print("✅ Representaciones string funcionan correctamente")
    print(f"   - SearchResult: {len(result_str)} caracteres")
    print(f"   - SearchQuery: {len(query_str)} caracteres")


def run_all_tests():
    """Ejecutar todos los tests de entidades Music Search"""
    print("🧪 TESTS DE ENTIDADES MUSIC SEARCH")
    print("=" * 55)

    tests = [
        test_search_result_entity_creation,
        test_search_result_entity_minimal_data,
        test_search_query_entity_creation,
        test_search_response_entity_creation,
        test_youtube_video_info_creation,
        test_music_track_data_creation,
        test_entity_string_representations,
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

    print("=" * 55)
    print(f"📊 RESULTADOS: {passed} pasaron, {failed} fallaron")

    if failed == 0:
        print("🎉 ¡Todos los tests de entidades Music Search pasaron!")
    else:
        print("⚠️ Algunos tests fallaron")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
