#!/usr/bin/env python
import os
import sys
import django
import re
import yt_dlp

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
sys.path.append('.')
sys.path.append('./src')
django.setup()

from apps.songs.infrastructure.models import SongModel
from apps.artists.infrastructure.models import ArtistModel
import uuid

def extract_artist_from_youtube_title(title):
    """Extrae el artista del título de YouTube"""
    # Patrones comunes de títulos de YouTube
    patterns = [
        r'^([^-]+) - (.+)$',  # "Artist - Song"
        r'^(.+) - (.+)$',     # "Artist - Song" 
        r'^([^|]+) \| (.+)$', # "Artist | Song"
        r'^(.+) ft\.? (.+) - (.+)$', # "Artist ft. Other - Song"
        r'^(.+) \(Official .+\)$',   # "Artist (Official Video/Audio)"
        r'^(.+) by (.+)$',    # "Song by Artist"
    ]
    
    for pattern in patterns:
        match = re.match(pattern, title, re.IGNORECASE)
        if match:
            groups = match.groups()
            if len(groups) >= 2:
                # Generalmente el primer grupo es el artista
                artist = groups[0].strip()
                # Limpiar el nombre del artista
                artist = re.sub(r'\s*\(Official.*\).*$', '', artist, flags=re.IGNORECASE)
                artist = re.sub(r'\s*-\s*Topic$', '', artist, flags=re.IGNORECASE)
                return artist
    
    return None

def fix_songs_artists(limit=5):
    """Arregla artistas de canciones sin artista"""
    
    print(f"🎵 Arreglando artistas de canciones...")
    
    songs_without_artist = SongModel.objects.filter(
        artist__isnull=True,
        source_type='youtube'
    )[:limit]
    
    print(f"Encontradas {songs_without_artist.count()} canciones sin artista")
    
    fixed_count = 0
    
    for song in songs_without_artist:
        print(f"\n🔍 Procesando: {song.title}")
        
        try:
            # Extraer información de YouTube
            if song.source_id:
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    try:
                        info = ydl.extract_info(
                            f'https://www.youtube.com/watch?v={song.source_id}', 
                            download=False
                        )
                        
                        youtube_title = info.get('title', '')
                        uploader = info.get('uploader', '')
                        
                        print(f"   YouTube título: {youtube_title}")
                        print(f"   Uploader: {uploader}")
                        
                        # Intentar extraer artista del título
                        artist_name = extract_artist_from_youtube_title(youtube_title)
                        
                        if not artist_name and uploader:
                            # Usar el uploader como artista si no se pudo extraer
                            artist_name = uploader.replace(' - Topic', '').replace('VEVO', '').strip()
                        
                        if artist_name and len(artist_name) > 1:
                            # Crear o buscar el artista
                            artist, created = ArtistModel.objects.get_or_create(
                                name=artist_name,
                                defaults={
                                    'id': uuid.uuid4(),
                                    'biography': f'Artist imported from YouTube',
                                    'image_url': ''
                                }
                            )
                            
                            # Asignar artista a la canción
                            song.artist = artist
                            song.save()
                            
                            print(f"   ✅ Artista asignado: {artist_name} ({'creado' if created else 'existente'})")
                            fixed_count += 1
                        else:
                            print(f"   ❌ No se pudo extraer artista")
                            
                    except Exception as e:
                        print(f"   ❌ Error con YouTube: {str(e)}")
                        
        except Exception as e:
            print(f"   ❌ Error general: {str(e)}")
    
    print(f"\n🎉 Proceso completado: {fixed_count} canciones arregladas")
    return fixed_count

if __name__ == '__main__':
    fix_songs_artists(10)  # Arreglar las primeras 10 canciones
