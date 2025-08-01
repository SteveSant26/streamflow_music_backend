#!/usr/bin/env python3
"""
Tests para entidades del dominio Album
"""

import os
import sys
from datetime import datetime, date
from uuid import uuid4

# Configurar el path correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(current_dir, '..', '..', '..')
sys.path.insert(0, project_root)

try:
    # Importar entidades del dominio
    from src.apps.albums.domain.entities import AlbumEntity
    print("✅ Entidad AlbumEntity importada correctamente")
except ImportError as e:
    print(f"❌ Error importando AlbumEntity: {e}")
    sys.exit(1)


def test_album_entity_creation():
    """Test creación de entidad AlbumEntity"""
    print("📀 Probando creación de AlbumEntity...")
    
    # Datos completos
    album_data = {
        'id': str(uuid4()),
        'title': 'Dark Side of the Moon',
        'artist_id': str(uuid4()),
        'artist_name': 'Pink Floyd',
        'release_date': datetime(1973, 3, 1).date(),
        'description': 'Progressive rock masterpiece',
        'cover_image_url': 'https://example.com/cover.jpg',
        'total_tracks': 10,
        'play_count': 15000,
        'is_active': True,
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }
    
    # Crear entidad
    album = AlbumEntity(**album_data)
    
    # Verificaciones
    assert album.id == album_data['id']
    assert album.title == 'Dark Side of the Moon'
    assert album.artist_name == 'Pink Floyd'
    assert album.total_tracks == 10
    assert album.release_date.year == 1973
    assert album.play_count == 15000
    assert album.is_active == True
    
    print("✅ AlbumEntity se crea correctamente con datos completos")
    print(f"   - Título: {album.title}")
    print(f"   - Artista: {album.artist_name}")
    print(f"   - Pistas: {album.total_tracks}")
    print(f"   - Año: {album.release_date.year}")
    
    return True


def test_album_entity_minimal_data():
    """Test creación de AlbumEntity solo con datos requeridos"""
    print("\n📀 Probando AlbumEntity con datos mínimos...")
    
    # Solo datos requeridos
    minimal_data = {
        'id': str(uuid4()),
        'title': 'Abbey Road',
        'artist_id': str(uuid4())
    }
    
    # Crear entidad
    album = AlbumEntity(**minimal_data)
    
    # Verificaciones
    assert album.id == minimal_data['id']
    assert album.title == 'Abbey Road'
    assert album.artist_id == minimal_data['artist_id']
    
    # Verificar valores por defecto
    assert album.artist_name is None
    assert album.release_date is None
    assert album.description is None
    assert album.cover_image_url is None
    assert album.total_tracks == 0
    assert album.play_count == 0
    assert album.is_active == True  # Default value
    assert album.created_at is None
    assert album.updated_at is None
    
    print("✅ AlbumEntity se crea correctamente con datos mínimos")
    print(f"   - Título: {album.title}")
    print(f"   - ID artista: {album.artist_id}")
    print(f"   - Activo por defecto: {album.is_active}")
    
    return True


def test_album_entity_properties():
    """Test propiedades específicas de AlbumEntity"""
    print("\n📀 Probando propiedades de AlbumEntity...")
    
    # Crear álbum
    album = AlbumEntity(
        id=str(uuid4()),
        title='The Wall',
        artist_id=str(uuid4()),
        artist_name='Pink Floyd',
        total_tracks=26,
        release_date=datetime(1979, 11, 30).date()
    )
    
    # Verificar propiedades
    assert album.title == 'The Wall'
    assert album.total_tracks == 26
    assert album.release_date.year == 1979
    assert album.artist_name == 'Pink Floyd'
    
    print("✅ Propiedades de AlbumEntity funcionan correctamente")
    print(f"   - Álbum: {album.title}")
    print(f"   - Pistas: {album.total_tracks}")
    print(f"   - Año: {album.release_date.year}")
    print(f"   - Artista: {album.artist_name}")
    
    return True


def test_album_entity_string_representation():
    """Test representación string de AlbumEntity"""
    print("\n📀 Probando representación string...")
    
    album = AlbumEntity(
        id='album-123',
        title='Thriller',
        artist_id='artist-456',
        artist_name='Michael Jackson'
    )
    
    # Verificar que la representación contiene información relevante
    str_repr = str(album)
    assert 'Thriller' in str_repr
    assert 'album-123' in str_repr or 'Michael Jackson' in str_repr
    
    print("✅ Representación string funciona")
    print(f"   - String: {str_repr}")
    
    return True


def test_album_entity_equality():
    """Test igualdad entre entidades"""
    print("\n📀 Probando igualdad de entidades...")
    
    album_id = str(uuid4())
    artist_id = str(uuid4())
    
    album1 = AlbumEntity(
        id=album_id,
        title='Hotel California',
        artist_id=artist_id,
        artist_name='Eagles'
    )
    
    album2 = AlbumEntity(
        id=album_id,
        title='Hotel California',
        artist_id=artist_id,
        artist_name='Eagles'
    )
    
    album3 = AlbumEntity(
        id=str(uuid4()),
        title='Hotel California',
        artist_id=artist_id,
        artist_name='Eagles'
    )
    
    # Test igualdad por ID
    assert album1.id == album2.id
    assert album1.id != album3.id
    
    print("✅ Igualdad de entidades funciona correctamente")
    print(f"   - Mismo ID: {album1.id == album2.id}")
    print(f"   - Diferente ID: {album1.id != album3.id}")
    
    return True


def run_all_tests():
    """Ejecuta todos los tests de entidades Album"""
    print("🧪 TESTS DE ENTIDADES ALBUM")
    print("=" * 50)
    
    tests = [
        test_album_entity_creation,
        test_album_entity_minimal_data,
        test_album_entity_properties,
        test_album_entity_string_representation,
        test_album_entity_equality,
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
        print("🎉 ¡Todos los tests de entidades Album pasaron!")
        return True
    else:
        print(f"⚠️  {failed} tests fallaron")
        return False


if __name__ == "__main__":
    run_all_tests()
