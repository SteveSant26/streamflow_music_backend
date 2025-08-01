"""
Tests para repositorio de Songs
"""
import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from django.test import TestCase
import uuid

# Configurar path antes de importar
import sys
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(BASE_DIR / 'src'))

from apps.songs.domain.entities import SongEntity
from apps.songs.infrastructure.repository.song_repository import SongRepository
from apps.songs.infrastructure.models.song_model import Song


class TestSongRepository(TestCase):
    """Tests para el repositorio de canciones"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        self.repository = SongRepository()
        
        # Datos de prueba para entidad
        self.sample_entity = SongEntity(
            id='song-123',
            title='Test Song',
            album_id='album-456',
            artist_id='artist-789',
            genre_id='genre-101',
            album_title='Test Album',
            artist_name='Test Artist',
            genre_name='Rock',
            duration_seconds=180,
            track_number=1,
            file_url='https://example.com/song.mp3',
            thumbnail_url='https://example.com/thumb.jpg',
            lyrics='Test lyrics',
            tags=['rock', 'classic'],
            play_count=100,
            favorite_count=10,
            download_count=5,
            source_type='youtube',
            source_id='youtube-123',
            source_url='https://youtube.com/watch?v=123',
            is_explicit=False,
            is_active=True,
            is_premium=False,
            audio_quality='standard',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Datos de prueba para modelo Django
        self.sample_model_data = {
            'title': 'Test Song',
            'album_id': uuid.UUID('12345678-1234-5678-9012-123456789012'),
            'artist_id': uuid.UUID('12345678-1234-5678-9012-123456789013'),
            'genre_id': uuid.UUID('12345678-1234-5678-9012-123456789014'),
            'album_title': 'Test Album',
            'artist_name': 'Test Artist',
            'genre_name': 'Rock',
            'duration_seconds': 180,
            'track_number': 1,
            'file_url': 'https://example.com/song.mp3',
            'thumbnail_url': 'https://example.com/thumb.jpg',
            'lyrics': 'Test lyrics',
            'tags': ['rock', 'classic'],
            'play_count': 100,
            'favorite_count': 10,
            'download_count': 5,
            'source_type': 'youtube',
            'source_id': 'youtube-123',
            'source_url': 'https://youtube.com/watch?v=123',
            'is_explicit': False,
            'is_active': True,
            'is_premium': False,
            'audio_quality': 'standard'
        }
    
    async def test_save_new_song(self):
        """Test guardar nueva canción"""
        # Arrange
        with patch('apps.songs.infrastructure.repository.song_repository.sync_to_async') as mock_sync:
            mock_song_model = Mock()
            mock_song_model.id = uuid.uuid4()
            mock_song_model.created_at = datetime.now()
            mock_song_model.updated_at = datetime.now()
            
            # Configurar el mock para create
            mock_create = AsyncMock(return_value=mock_song_model)
            mock_sync.side_effect = lambda func: mock_create
            
            # Act
            result = await self.repository.save(self.sample_entity)
            
            # Assert
            self.assertIsInstance(result, SongEntity)
            mock_sync.assert_called()
    
    def test_song_model_creation(self):
        """Test crear modelo Django directamente"""
        song = Song.objects.create(**self.sample_model_data)
        
        self.assertEqual(song.title, 'Test Song')
        self.assertEqual(song.artist_name, 'Test Artist')
        self.assertEqual(song.album_title, 'Test Album')
        self.assertEqual(song.genre_name, 'Rock')
        self.assertEqual(song.duration_seconds, 180)
        self.assertEqual(song.play_count, 100)
        self.assertEqual(song.tags, ['rock', 'classic'])
        self.assertTrue(song.is_active)
        self.assertFalse(song.is_explicit)
    
    async def test_get_by_id_existing(self):
        """Test obtener canción por ID existente"""
        # Crear canción en la BD
        song_model = Song.objects.create(**self.sample_model_data)
        
        with patch('apps.songs.infrastructure.repository.song_repository.sync_to_async') as mock_sync:
            # Configurar mock para get
            mock_get = AsyncMock(return_value=song_model)
            mock_sync.side_effect = lambda func: mock_get
            
            # Act
            result = await self.repository.get_by_id(str(song_model.id))
            
            # Assert
            mock_sync.assert_called()
    
    async def test_get_by_id_not_found(self):
        """Test obtener canción por ID no existente"""
        with patch('apps.songs.infrastructure.repository.song_repository.sync_to_async') as mock_sync:
            # Configurar mock para que lance DoesNotExist
            from django.core.exceptions import ObjectDoesNotExist
            mock_get = AsyncMock(side_effect=ObjectDoesNotExist())
            mock_sync.side_effect = lambda func: mock_get
            
            # Act
            result = await self.repository.get_by_id('non-existent-id')
            
            # Assert
            self.assertIsNone(result)
    
    def test_entity_to_model_conversion(self):
        """Test conversión de entidad a datos de modelo"""
        # Este test verifica que los datos de la entidad se mapeen correctamente
        song = Song.objects.create(
            title=self.sample_entity.title,
            artist_name=self.sample_entity.artist_name,
            album_title=self.sample_entity.album_title,
            genre_name=self.sample_entity.genre_name,
            duration_seconds=self.sample_entity.duration_seconds,
            play_count=self.sample_entity.play_count,
            favorite_count=self.sample_entity.favorite_count,
            download_count=self.sample_entity.download_count,
            tags=self.sample_entity.tags,
            is_active=self.sample_entity.is_active,
            is_explicit=self.sample_entity.is_explicit,
            is_premium=self.sample_entity.is_premium,
            source_type=self.sample_entity.source_type,
            source_id=self.sample_entity.source_id,
            audio_quality=self.sample_entity.audio_quality
        )
        
        # Verificar que se guardó correctamente
        self.assertEqual(song.title, self.sample_entity.title)
        self.assertEqual(song.artist_name, self.sample_entity.artist_name)
        self.assertEqual(song.play_count, self.sample_entity.play_count)
        self.assertEqual(song.tags, self.sample_entity.tags)
    
    def test_model_to_entity_conversion_concept(self):
        """Test concepto de conversión de modelo a entidad"""
        # Crear modelo en BD
        song_model = Song.objects.create(**self.sample_model_data)
        
        # Simular conversión manual (como haría el repositorio)
        entity_data = {
            'id': str(song_model.id),
            'title': song_model.title,
            'artist_name': song_model.artist_name,
            'album_title': song_model.album_title,
            'genre_name': song_model.genre_name,
            'duration_seconds': song_model.duration_seconds,
            'play_count': song_model.play_count,
            'favorite_count': song_model.favorite_count,
            'download_count': song_model.download_count,
            'tags': song_model.tags,
            'is_active': song_model.is_active,
            'is_explicit': song_model.is_explicit,
            'is_premium': song_model.is_premium,
            'source_type': song_model.source_type,
            'source_id': song_model.source_id,
            'audio_quality': song_model.audio_quality,
            'created_at': song_model.created_at,
            'updated_at': song_model.updated_at
        }
        
        # Crear entidad desde datos del modelo
        entity = SongEntity(**entity_data)
        
        # Verificar conversión
        self.assertEqual(entity.title, song_model.title)
        self.assertEqual(entity.artist_name, song_model.artist_name)
        self.assertEqual(entity.play_count, song_model.play_count)
        self.assertEqual(entity.tags, song_model.tags)
    
    async def test_search_songs_concept(self):
        """Test concepto de búsqueda de canciones"""
        # Crear canciones de prueba
        songs_data = [
            {**self.sample_model_data, 'title': 'Rock Song 1', 'genre_name': 'Rock'},
            {**self.sample_model_data, 'title': 'Pop Song 1', 'genre_name': 'Pop'},
            {**self.sample_model_data, 'title': 'Rock Ballad', 'genre_name': 'Rock'},
        ]
        
        created_songs = []
        for data in songs_data:
            song = Song.objects.create(**data)
            created_songs.append(song)
        
        # Test búsqueda por título
        rock_songs = Song.objects.filter(title__icontains='rock')
        self.assertEqual(rock_songs.count(), 2)
        
        # Test búsqueda por género
        rock_genre_songs = Song.objects.filter(genre_name='Rock')
        self.assertEqual(rock_genre_songs.count(), 2)
        
        # Test búsqueda por artista
        artist_songs = Song.objects.filter(artist_name=self.sample_model_data['artist_name'])
        self.assertEqual(artist_songs.count(), 3)
    
    async def test_get_random_songs_concept(self):
        """Test concepto de obtener canciones aleatorias"""
        # Crear varias canciones
        for i in range(5):
            data = self.sample_model_data.copy()
            data['title'] = f'Random Song {i}'
            Song.objects.create(**data)
        
        # Obtener canciones aleatorias
        random_songs = Song.objects.filter(is_active=True).order_by('?')[:3]
        
        # Verificar que se obtuvieron canciones
        self.assertLessEqual(len(random_songs), 3)
        self.assertGreater(len(random_songs), 0)
        
        # Verificar que todas están activas
        for song in random_songs:
            self.assertTrue(song.is_active)
    
    async def test_get_by_source_concept(self):
        """Test concepto de obtener canción por fuente externa"""
        # Crear canción con source específico
        data = self.sample_model_data.copy()
        data['source_type'] = 'youtube'
        data['source_id'] = 'unique-youtube-id'
        
        song = Song.objects.create(**data)
        
        # Buscar por source
        found_song = Song.objects.filter(
            source_type='youtube',
            source_id='unique-youtube-id'
        ).first()
        
        self.assertIsNotNone(found_song)
        self.assertEqual(found_song.id, song.id)
        self.assertEqual(found_song.source_id, 'unique-youtube-id')
    
    def test_repository_inheritance(self):
        """Test que el repositorio implementa la interfaz correcta"""
        from apps.songs.domain.repository.Isong_repository import ISongRepository
        from common.mixins.logging_mixin import LoggingMixin
        
        # Verificar herencia
        self.assertIsInstance(self.repository, ISongRepository)
        self.assertIsInstance(self.repository, LoggingMixin)
        
        # Verificar que tiene los métodos requeridos
        self.assertTrue(hasattr(self.repository, 'save'))
        self.assertTrue(hasattr(self.repository, 'get_by_id'))
        self.assertTrue(callable(getattr(self.repository, 'save')))
        self.assertTrue(callable(getattr(self.repository, 'get_by_id')))
    
    def test_repository_logging_capability(self):
        """Test capacidad de logging del repositorio"""
        # Verificar que tiene logger
        self.assertTrue(hasattr(self.repository, 'logger'))
        self.assertIsNotNone(self.repository.logger)
        
        # Verificar métodos de logging
        self.assertTrue(hasattr(self.repository, 'log_info'))
        self.assertTrue(hasattr(self.repository, 'log_error'))
        self.assertTrue(hasattr(self.repository, 'log_warning'))
    
    def test_song_filtering_and_ordering(self):
        """Test filtrado y ordenamiento de canciones"""
        # Crear canciones con diferentes métricas
        songs_data = [
            {**self.sample_model_data, 'title': 'Popular Song', 'play_count': 1000},
            {**self.sample_model_data, 'title': 'Unpopular Song', 'play_count': 10},
            {**self.sample_model_data, 'title': 'Medium Song', 'play_count': 500},
        ]
        
        for data in songs_data:
            Song.objects.create(**data)
        
        # Test ordenamiento por popularidad (descendente)
        popular_songs = Song.objects.filter(is_active=True).order_by('-play_count')
        
        self.assertEqual(popular_songs[0].title, 'Popular Song')
        self.assertEqual(popular_songs[1].title, 'Medium Song')
        self.assertEqual(popular_songs[2].title, 'Unpopular Song')
        
        # Test filtrado por umbral de popularidad
        very_popular = Song.objects.filter(play_count__gte=800)
        self.assertEqual(very_popular.count(), 1)
        self.assertEqual(very_popular[0].title, 'Popular Song')


if __name__ == '__main__':
    unittest.main()
