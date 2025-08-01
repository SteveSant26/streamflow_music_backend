#!/usr/bin/env python
"""
Test directo para verificar que las entidades de Songs funcionan
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Configurar paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / 'src'))

# Configurar Django con env de desarrollo
from dotenv import load_dotenv
load_dotenv(BASE_DIR / 'config' / 'settings' / '.env.dev')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

import django
django.setup()

# Importar después de setup
from apps.songs.domain.entities import SongEntity


def test_song_entity_creation():
    """Test básico de creación de entidad Song"""
    print("🎵 Probando creación de SongEntity...")
    
    # Datos de prueba
    song_data = {
        'id': 'song-test-123',
        'title': 'Test Song',
        'artist_name': 'Test Artist',
        'album_title': 'Test Album',
        'genre_name': 'Rock',
        'duration_seconds': 180,
        'play_count': 100,
        'is_active': True
    }
    
    # Crear entidad
    song = SongEntity(**song_data)
    
    # Verificaciones
    assert song.id == 'song-test-123'
    assert song.title == 'Test Song'
    assert song.artist_name == 'Test Artist'
    assert song.duration_seconds == 180
    assert song.play_count == 100
    assert song.is_active == True
    assert song.tags == []  # Se inicializa vacío
    
    print("✅ SongEntity creada correctamente")
    print(f"   - ID: {song.id}")
    print(f"   - Título: {song.title}")
    print(f"   - Artista: {song.artist_name}")
    print(f"   - Duración: {song.duration_seconds}s")
    
    return True


def test_song_entity_minimal():
    """Test con datos mínimos"""
    print("\n🎵 Probando SongEntity con datos mínimos...")
    
    song = SongEntity(id='minimal-song', title='Minimal Test')
    
    assert song.id == 'minimal-song'
    assert song.title == 'Minimal Test'
    assert song.duration_seconds == 0
    assert song.play_count == 0
    assert song.is_active == True
    assert song.tags == []
    
    print("✅ SongEntity mínima creada correctamente")
    
    return True


def test_song_entity_tags():
    """Test inicialización de tags"""
    print("\n🎵 Probando inicialización de tags...")
    
    # Con tags
    song_with_tags = SongEntity(
        id='tagged-song',
        title='Tagged Song',
        tags=['rock', 'classic']
    )
    
    assert song_with_tags.tags == ['rock', 'classic']
    
    # Sin tags (debería inicializar vacío)
    song_no_tags = SongEntity(
        id='untagged-song',
        title='Untagged Song'
    )
    
    assert song_no_tags.tags == []
    
    print("✅ Tags funcionan correctamente")
    
    return True


def main():
    """Función principal"""
    print("🚀 Iniciando tests directos de Songs...")
    print("=" * 50)
    
    try:
        # Ejecutar tests
        test_song_entity_creation()
        test_song_entity_minimal()
        test_song_entity_tags()
        
        print("\n" + "=" * 50)
        print("🎉 ¡Todos los tests pasaron correctamente!")
        print("✅ Las entidades de Songs funcionan bien")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error en los tests: {str(e)}")
        print(f"❌ Tipo de error: {type(e).__name__}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
