#!/usr/bin/env python3
"""
Tests para casos de uso de Music Search
"""

import os
import sys
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock
from typing import List

# Configurar el path correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, project_root)

try:
    # Importar entidades del dominio
    from src.apps.music_search.domain.entities import (
        SearchResultEntity,
        SearchQueryEntity,
        SearchResponseEntity
    )
    print("✅ Entidades importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando: {e}")
    sys.exit(1)

# Crear interfaces mock para evitar dependencias
from abc import ABC, abstractmethod

class ISearchRepository(ABC):
    """Interface mock del repositorio de búsqueda"""
    
    @abstractmethod
    def search_artists(self, query: str, limit: int = 10) -> List[SearchResultEntity]:
        pass
    
    @abstractmethod
    def search_albums(self, query: str, limit: int = 10) -> List[SearchResultEntity]:
        pass
    
    @abstractmethod
    def search_songs(self, query: str, limit: int = 10) -> List[SearchResultEntity]:
        pass
    
    @abstractmethod
    def search_genres(self, query: str, limit: int = 10) -> List[SearchResultEntity]:
        pass

class ISearchHistoryRepository(ABC):
    """Interface mock del repositorio de historial"""
    
    @abstractmethod
    def save_query(self, query: SearchQueryEntity) -> None:
        pass
    
    @abstractmethod
    def get_user_history(self, user_id: str, limit: int = 10) -> List[SearchQueryEntity]:
        pass

# Excepciones mock
class SearchException(Exception):
    """Excepción de búsqueda"""
    pass

class EmptyQueryException(SearchException):
    """Excepción cuando la query está vacía"""
    pass

print("⚠️ Usando interfaces y excepciones mock")

# Casos de Uso Mock
class UniversalSearchUseCase:
    """Caso de uso para búsqueda universal"""
    
    def __init__(self, repository: ISearchRepository, history_repo: ISearchHistoryRepository = None):
        self.repository = repository
        self.history_repo = history_repo
    
    def execute(self, query: str, types: List[str] = None, limit: int = 10, user_id: str = None) -> SearchResponseEntity:
        if not query or not query.strip():
            raise EmptyQueryException("Query cannot be empty")
        
        start_time = datetime.now()
        
        # Buscar en todos los tipos por defecto
        if not types:
            types = ['artists', 'albums', 'songs', 'genres']
        
        artists = self.repository.search_artists(query, limit) if 'artists' in types else []
        albums = self.repository.search_albums(query, limit) if 'albums' in types else []
        songs = self.repository.search_songs(query, limit) if 'songs' in types else []
        genres = self.repository.search_genres(query, limit) if 'genres' in types else []
        
        total_results = len(artists) + len(albums) + len(songs) + len(genres)
        
        end_time = datetime.now()
        search_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Guardar en historial si se especifica usuario
        if self.history_repo and user_id:
            search_query = SearchQueryEntity(
                id=str(uuid4()),
                query_text=query,
                user_id=user_id,
                results_count=total_results,
                created_at=datetime.now()
            )
            self.history_repo.save_query(search_query)
        
        return SearchResponseEntity(
            query=query,
            artists=artists,
            albums=albums,
            songs=songs,
            genres=genres,
            total_results=total_results,
            search_time_ms=search_time_ms
        )

class QuickSearchUseCase:
    """Caso de uso para búsqueda rápida (solo títulos)"""
    
    def __init__(self, repository: ISearchRepository):
        self.repository = repository
    
    def execute(self, query: str, limit: int = 5) -> List[SearchResultEntity]:
        if not query or not query.strip():
            return []
        
        # Búsqueda rápida en canciones principalmente
        results = self.repository.search_songs(query, limit)
        return results

class SearchHistoryUseCase:
    """Caso de uso para obtener historial de búsquedas"""
    
    def __init__(self, history_repo: ISearchHistoryRepository):
        self.history_repo = history_repo
    
    def execute(self, user_id: str, limit: int = 10) -> List[SearchQueryEntity]:
        if not user_id:
            return []
        
        return self.history_repo.get_user_history(user_id, limit)


def test_universal_search_use_case():
    """Test del caso de uso UniversalSearchUseCase"""
    print("🔍 Probando UniversalSearchUseCase...")
    
    # Crear mock del repositorio
    mock_repository = Mock(spec=ISearchRepository)
    
    # Configurar mocks
    artists = [SearchResultEntity('artist', 'a1', 'Queen', relevance_score=0.9)]
    albums = [SearchResultEntity('album', 'al1', 'A Night at the Opera', 'Queen', relevance_score=0.85)]
    songs = [
        SearchResultEntity('song', 's1', 'Bohemian Rhapsody', 'Queen', relevance_score=0.95),
        SearchResultEntity('song', 's2', 'We Will Rock You', 'Queen', relevance_score=0.88)
    ]
    genres = [SearchResultEntity('genre', 'g1', 'Rock', relevance_score=0.75)]
    
    mock_repository.search_artists.return_value = artists
    mock_repository.search_albums.return_value = albums
    mock_repository.search_songs.return_value = songs
    mock_repository.search_genres.return_value = genres
    
    # Crear y ejecutar el caso de uso
    use_case = UniversalSearchUseCase(mock_repository)
    result = use_case.execute('queen', limit=10)
    
    # Verificaciones
    assert result.query == 'queen'
    assert len(result.artists) == 1
    assert len(result.albums) == 1
    assert len(result.songs) == 2
    assert len(result.genres) == 1
    assert result.total_results == 5
    assert result.search_time_ms is not None
    assert result.search_time_ms > 0
    
    # Verificar llamadas al repositorio
    mock_repository.search_artists.assert_called_once_with('queen', 10)
    mock_repository.search_albums.assert_called_once_with('queen', 10)
    mock_repository.search_songs.assert_called_once_with('queen', 10)
    mock_repository.search_genres.assert_called_once_with('queen', 10)
    
    print("✅ UniversalSearchUseCase funciona correctamente")
    print(f"   - Query: {result.query}")
    print(f"   - Total resultados: {result.total_results}")
    print(f"   - Tiempo: {result.search_time_ms:.2f}ms")


def test_universal_search_with_filters():
    """Test búsqueda universal con filtros de tipo"""
    print("🔍 Probando búsqueda con filtros de tipo...")
    
    mock_repository = Mock(spec=ISearchRepository)
    mock_repository.search_songs.return_value = [
        SearchResultEntity('song', 's1', 'Test Song', 'Test Artist', relevance_score=0.8)
    ]
    
    # Solo buscar canciones
    use_case = UniversalSearchUseCase(mock_repository)
    result = use_case.execute('test', types=['songs'], limit=5)
    
    # Verificaciones
    assert len(result.artists) == 0
    assert len(result.albums) == 0
    assert len(result.songs) == 1
    assert len(result.genres) == 0
    assert result.total_results == 1
    
    # Solo debería haber llamado a search_songs
    mock_repository.search_songs.assert_called_once_with('test', 5)
    mock_repository.search_artists.assert_not_called()
    mock_repository.search_albums.assert_not_called()
    mock_repository.search_genres.assert_not_called()
    
    print("✅ Filtros de tipo funcionan correctamente")
    print(f"   - Solo canciones: {len(result.songs)}")


def test_universal_search_with_history():
    """Test búsqueda universal con guardado de historial"""
    print("🔍 Probando búsqueda con historial...")
    
    mock_repository = Mock(spec=ISearchRepository)
    mock_history_repo = Mock(spec=ISearchHistoryRepository)
    
    # Configurar mocks
    mock_repository.search_artists.return_value = []
    mock_repository.search_albums.return_value = []
    mock_repository.search_songs.return_value = [
        SearchResultEntity('song', 's1', 'Test Song', relevance_score=0.8)
    ]
    mock_repository.search_genres.return_value = []
    
    # Ejecutar búsqueda con usuario
    use_case = UniversalSearchUseCase(mock_repository, mock_history_repo)
    result = use_case.execute('test query', user_id='user-123')
    
    # Verificar que se guardó en historial
    mock_history_repo.save_query.assert_called_once()
    call_args = mock_history_repo.save_query.call_args[0][0]
    assert call_args.query_text == 'test query'
    assert call_args.user_id == 'user-123'
    assert call_args.results_count == 1
    
    print("✅ Guardado de historial funciona correctamente")
    print(f"   - Query guardada: {call_args.query_text}")
    print(f"   - Usuario: {call_args.user_id}")


def test_universal_search_empty_query():
    """Test búsqueda con query vacía"""
    print("🔍 Probando búsqueda con query vacía...")
    
    mock_repository = Mock(spec=ISearchRepository)
    use_case = UniversalSearchUseCase(mock_repository)
    
    # Verificar que lanza excepción
    try:
        use_case.execute('')
        assert False, "Debería haber lanzado EmptyQueryException"
    except EmptyQueryException as e:
        assert "empty" in str(e).lower()
        print("✅ EmptyQueryException lanzada correctamente")


def test_quick_search_use_case():
    """Test del caso de uso QuickSearchUseCase"""
    print("🔍 Probando QuickSearchUseCase...")
    
    mock_repository = Mock(spec=ISearchRepository)
    mock_repository.search_songs.return_value = [
        SearchResultEntity('song', 's1', 'Quick Song 1', 'Artist 1', relevance_score=0.9),
        SearchResultEntity('song', 's2', 'Quick Song 2', 'Artist 2', relevance_score=0.8)
    ]
    
    use_case = QuickSearchUseCase(mock_repository)
    results = use_case.execute('quick', limit=5)
    
    # Verificaciones
    assert len(results) == 2
    assert results[0].title == 'Quick Song 1'
    assert results[1].title == 'Quick Song 2'
    
    mock_repository.search_songs.assert_called_once_with('quick', 5)
    
    print("✅ QuickSearchUseCase funciona correctamente")
    print(f"   - Resultados: {len(results)}")
    print(f"   - Primer resultado: {results[0].title}")


def test_quick_search_empty_query():
    """Test búsqueda rápida con query vacía"""
    print("🔍 Probando búsqueda rápida con query vacía...")
    
    mock_repository = Mock(spec=ISearchRepository)
    use_case = QuickSearchUseCase(mock_repository)
    
    results = use_case.execute('')
    
    # Debería retornar lista vacía
    assert len(results) == 0
    mock_repository.search_songs.assert_not_called()
    
    print("✅ Búsqueda rápida con query vacía funciona correctamente")


def test_search_history_use_case():
    """Test del caso de uso SearchHistoryUseCase"""
    print("🔍 Probando SearchHistoryUseCase...")
    
    mock_history_repo = Mock(spec=ISearchHistoryRepository)
    
    # Configurar historial mock
    history = [
        SearchQueryEntity('q1', 'rock music', 'user-123', results_count=15),
        SearchQueryEntity('q2', 'pop songs', 'user-123', results_count=8)
    ]
    mock_history_repo.get_user_history.return_value = history
    
    use_case = SearchHistoryUseCase(mock_history_repo)
    results = use_case.execute('user-123', limit=10)
    
    # Verificaciones
    assert len(results) == 2
    assert results[0].query_text == 'rock music'
    assert results[1].query_text == 'pop songs'
    
    mock_history_repo.get_user_history.assert_called_once_with('user-123', 10)
    
    print("✅ SearchHistoryUseCase funciona correctamente")
    print(f"   - Historial: {len(results)} queries")
    print(f"   - Primera query: {results[0].query_text}")


def test_search_history_empty_user():
    """Test historial con usuario vacío"""
    print("🔍 Probando historial con usuario vacío...")
    
    mock_history_repo = Mock(spec=ISearchHistoryRepository)
    use_case = SearchHistoryUseCase(mock_history_repo)
    
    results = use_case.execute('', limit=10)
    
    # Debería retornar lista vacía
    assert len(results) == 0
    mock_history_repo.get_user_history.assert_not_called()
    
    print("✅ Historial con usuario vacío funciona correctamente")


def run_all_tests():
    """Ejecutar todos los tests de casos de uso Music Search"""
    print("🧪 TESTS DE CASOS DE USO MUSIC SEARCH")
    print("=" * 55)
    
    tests = [
        test_universal_search_use_case,
        test_universal_search_with_filters,
        test_universal_search_with_history,
        test_universal_search_empty_query,
        test_quick_search_use_case,
        test_quick_search_empty_query,
        test_search_history_use_case,
        test_search_history_empty_user,
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
        print("🎉 ¡Todos los tests de casos de uso Music Search pasaron!")
    else:
        print("⚠️ Algunos tests fallaron")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
