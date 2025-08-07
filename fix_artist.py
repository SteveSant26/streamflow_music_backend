#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
sys.path.append('.')
sys.path.append('./src')
django.setup()

from apps.songs.infrastructure.models import SongModel
from apps.artists.infrastructure.models import ArtistModel
import uuid

def fix_billie_eilish_song():
    """Arregla la canción de Billie Eilish asignándole el artista correcto"""
    
    # Buscar o crear el artista Billie Eilish
    artist, created = ArtistModel.objects.get_or_create(
        name='Billie Eilish',
        defaults={
            'id': uuid.uuid4(),
            'biography': 'American singer-songwriter',
            'image_url': ''
        }
    )
    
    print(f'Artista {"creado" if created else "encontrado"}: {artist.name}')
    
    # Actualizar la canción
    song = SongModel.objects.get(id='ba449813-b9d7-4e83-ab2f-63024765ed22')
    song.artist = artist
    song.save()
    
    print(f'Canción actualizada: {song.title} - {song.artist.name}')
    
    # Probar las letras ahora
    import asyncio
    from apps.songs.use_cases.lyrics_use_cases import GetSongLyricsUseCase
    
    use_case = GetSongLyricsUseCase()
    result = asyncio.run(use_case.execute(str(song.id), True))
    
    if result:
        print(f'¡Letras encontradas! Longitud: {len(result)} caracteres')
        print('Primeras líneas:')
        print(result[:200] + '...')
    else:
        print('No se encontraron letras')

if __name__ == '__main__':
    fix_billie_eilish_song()
