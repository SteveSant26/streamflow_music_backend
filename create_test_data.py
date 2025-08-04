#!/usr/bin/env python3
"""
Script para crear datos de prueba para las playlists
"""
import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from django.contrib.auth.models import User
from src.apps.user_profile.models import UserProfileModel
from src.apps.songs.models import SongModel, ArtistModel, AlbumModel
from src.apps.genres.models import GenreModel


def create_test_data():
    """Crear datos de prueba"""
    print("Creando datos de prueba...")
    
    # Crear usuario de prueba
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Usuario creado: {user.username}")
    else:
        print(f"ℹ️ Usuario ya existe: {user.username}")
    
    # Crear perfil de usuario
    profile, created = UserProfileModel.objects.get_or_create(
        user=user,
        defaults={'subscription_type': 'free'}
    )
    if created:
        print(f"✅ Perfil creado: {profile.id}")
    else:
        print(f"ℹ️ Perfil ya existe: {profile.id}")
    
    # Crear géneros de prueba
    genre_names = ['Pop', 'Rock', 'Jazz', 'Electronic', 'Classical']
    for genre_name in genre_names:
        genre, created = GenreModel.objects.get_or_create(
            name=genre_name,
            defaults={'description': f'Género {genre_name}'}
        )
        if created:
            print(f"✅ Género creado: {genre.name}")
    
    # Crear artistas de prueba
    artist_names = ['The Beatles', 'Queen', 'Pink Floyd', 'Led Zeppelin', 'The Rolling Stones']
    for artist_name in artist_names:
        artist, created = ArtistModel.objects.get_or_create(
            name=artist_name,
            defaults={
                'description': f'Descripción de {artist_name}',
                'country': 'Reino Unido'
            }
        )
        if created:
            print(f"✅ Artista creado: {artist.name}")
    
    # Crear álbumes de prueba
    albums_data = [
        ('Abbey Road', 'The Beatles'),
        ('Bohemian Rhapsody', 'Queen'),
        ('The Wall', 'Pink Floyd'),
        ('Led Zeppelin IV', 'Led Zeppelin'),
        ('Sticky Fingers', 'The Rolling Stones'),
    ]
    
    for album_name, artist_name in albums_data:
        try:
            artist = ArtistModel.objects.get(name=artist_name)
            album, created = AlbumModel.objects.get_or_create(
                title=album_name,
                artist=artist,
                defaults={
                    'description': f'Álbum {album_name}',
                    'release_date': '1970-01-01'
                }
            )
            if created:
                print(f"✅ Álbum creado: {album.title}")
        except ArtistModel.DoesNotExist:
            print(f"❌ Artista no encontrado: {artist_name}")
    
    # Crear canciones de prueba
    songs_data = [
        ('Come Together', 'Abbey Road', 'The Beatles', 'Rock'),
        ('Bohemian Rhapsody', 'Bohemian Rhapsody', 'Queen', 'Rock'),
        ('Another Brick in the Wall', 'The Wall', 'Pink Floyd', 'Rock'),
        ('Stairway to Heaven', 'Led Zeppelin IV', 'Led Zeppelin', 'Rock'),
        ('Paint It Black', 'Sticky Fingers', 'The Rolling Stones', 'Rock'),
    ]
    
    for song_title, album_title, artist_name, genre_name in songs_data:
        try:
            artist = ArtistModel.objects.get(name=artist_name)
            album = AlbumModel.objects.get(title=album_title, artist=artist)
            genre = GenreModel.objects.get(name=genre_name)
            
            song, created = SongModel.objects.get_or_create(
                title=song_title,
                album=album,
                defaults={
                    'duration': 240,  # 4 minutos
                    'youtube_url': f'https://youtube.com/watch?v=example_{song_title.replace(" ", "_").lower()}',
                    'genre': genre,
                    'explicit_content': False
                }
            )
            if created:
                print(f"✅ Canción creada: {song.title}")
        except (ArtistModel.DoesNotExist, AlbumModel.DoesNotExist, GenreModel.DoesNotExist) as e:
            print(f"❌ Error creando canción {song_title}: {e}")
    
    print(f"\n📊 Resumen:")
    print(f"- Usuarios: {User.objects.count()}")
    print(f"- Perfiles: {UserProfileModel.objects.count()}")
    print(f"- Géneros: {GenreModel.objects.count()}")
    print(f"- Artistas: {ArtistModel.objects.count()}")
    print(f"- Álbumes: {AlbumModel.objects.count()}")
    print(f"- Canciones: {SongModel.objects.count()}")


if __name__ == '__main__':
    create_test_data()
