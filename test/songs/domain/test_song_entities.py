"""
Tests para entidades del dominio de Songs
Archivo: src/apps/songs/domain/entities.py
"""

import pytest
import sys
import os
from datetime import datetime

# Añadir src/ al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from apps.songs.domain.entities import SongEntity


class TestSongEntity:
    """Tests para la entidad SongEntity"""
    
    def test_song_entity_creation_minimal(self):
        """Test creación de canción con datos mínimos"""
        song = SongEntity(
            id="song-1",
            title="Test Song"
        )
        
        assert song.id == "song-1"
        assert song.title == "Test Song"
        assert song.album_id is None
        assert song.artist_id is None
        assert song.genre_ids == []
        assert song.duration_seconds == 0
        assert song.play_count == 0
        assert song.favorite_count == 0
        assert song.download_count == 0
        assert song.source_type == "youtube"
        assert song.audio_quality == "standard"
        
    def test_song_entity_creation_complete(self):
        """Test creación de canción con datos completos"""
        release_date = datetime(2023, 1, 1)
        created_at = datetime.now()
        
        song = SongEntity(
            id="song-2",
            title="Complete Test Song",
            album_id="album-1",
            artist_id="artist-1",
            genre_ids=["rock", "pop"],
            duration_seconds=240,
            album_title="Test Album",
            artist_name="Test Artist",
            track_number=5,
            file_url="https://storage.supabase.co/test/song.mp3",
            thumbnail_url="https://storage.supabase.co/test/thumb.jpg",
            lyrics="Test lyrics for the song",
            play_count=100,
            favorite_count=50,
            download_count=25,
            source_type="upload",
            source_id="upload-123",
            source_url="https://example.com/original",
            audio_quality="high",
            created_at=created_at,
            release_date=release_date
        )
        
        assert song.id == "song-2"
        assert song.title == "Complete Test Song"
        assert song.album_id == "album-1"
        assert song.artist_id == "artist-1"
        assert song.genre_ids == ["rock", "pop"]
        assert song.duration_seconds == 240
        assert song.album_title == "Test Album"
        assert song.artist_name == "Test Artist"
        assert song.track_number == 5
        assert song.file_url == "https://storage.supabase.co/test/song.mp3"
        assert song.thumbnail_url == "https://storage.supabase.co/test/thumb.jpg"
        assert song.lyrics == "Test lyrics for the song"
        assert song.play_count == 100
        assert song.favorite_count == 50
        assert song.download_count == 25
        assert song.source_type == "upload"
        assert song.source_id == "upload-123"
        assert song.source_url == "https://example.com/original"
        assert song.audio_quality == "high"
        assert song.created_at == created_at
        assert song.release_date == release_date
        
    def test_song_entity_post_init_genre_ids(self):
        """Test que post_init inicializa genre_ids como lista vacía"""
        song1 = SongEntity(
            id="song-post-init-1",
            title="Test Song 1",
            genre_ids=None
        )
        assert song1.genre_ids == []
        
        song2 = SongEntity(
            id="song-post-init-2",
            title="Test Song 2",
            genre_ids=["rock"]
        )
        assert song2.genre_ids == ["rock"]
        
    def test_song_entity_duration_formats(self):
        """Test diferentes formatos de duración"""
        # Canción corta (30 segundos)
        short_song = SongEntity(
            id="song-short",
            title="Short Song",
            duration_seconds=30
        )
        assert short_song.duration_seconds == 30
        
        # Canción promedio (3:30 minutos)
        average_song = SongEntity(
            id="song-average",
            title="Average Song",
            duration_seconds=210
        )
        assert average_song.duration_seconds == 210
        
        # Canción larga (10 minutos)
        long_song = SongEntity(
            id="song-long",
            title="Long Song",
            duration_seconds=600
        )
        assert long_song.duration_seconds == 600
        
    def test_song_entity_metrics(self):
        """Test métricas de reproducción y favoritos"""
        song = SongEntity(
            id="song-metrics",
            title="Metrics Song",
            play_count=1000,
            favorite_count=200,
            download_count=50
        )
        
        assert song.play_count == 1000
        assert song.favorite_count == 200
        assert song.download_count == 50
        
    def test_song_entity_source_types(self):
        """Test diferentes tipos de fuente"""
        youtube_song = SongEntity(
            id="song-youtube",
            title="YouTube Song",
            source_type="youtube",
            source_id="youtube-123",
            source_url="https://youtube.com/watch?v=123"
        )
        
        upload_song = SongEntity(
            id="song-upload",
            title="Upload Song",
            source_type="upload",
            source_id="upload-456"
        )
        
        assert youtube_song.source_type == "youtube"
        assert youtube_song.source_id == "youtube-123"
        assert youtube_song.source_url == "https://youtube.com/watch?v=123"
        
        assert upload_song.source_type == "upload"
        assert upload_song.source_id == "upload-456"
        
    def test_song_entity_audio_quality(self):
        """Test diferentes calidades de audio"""
        standard_song = SongEntity(
            id="song-standard",
            title="Standard Quality Song",
            audio_quality="standard"
        )
        
        high_song = SongEntity(
            id="song-high",
            title="High Quality Song",
            audio_quality="high"
        )
        
        lossless_song = SongEntity(
            id="song-lossless",
            title="Lossless Quality Song",
            audio_quality="lossless"
        )
        
        assert standard_song.audio_quality == "standard"
        assert high_song.audio_quality == "high"
        assert lossless_song.audio_quality == "lossless"
        
    def test_song_entity_timestamps(self):
        """Test manejo de timestamps"""
        now = datetime.now()
        release_date = datetime(2023, 6, 15)
        last_played = datetime(2024, 1, 1)
        
        song = SongEntity(
            id="song-timestamps",
            title="Timestamps Song",
            created_at=now,
            updated_at=now,
            last_played_at=last_played,
            release_date=release_date
        )
        
        assert song.created_at == now
        assert song.updated_at == now
        assert song.last_played_at == last_played
        assert song.release_date == release_date
        
    def test_song_entity_optional_fields(self):
        """Test campos opcionales con None"""
        song = SongEntity(
            id="song-optional",
            title="Optional Fields Song",
            album_id=None,
            artist_id=None,
            album_title=None,
            artist_name=None,
            track_number=None,
            file_url=None,
            thumbnail_url=None,
            lyrics=None,
            source_id=None,
            source_url=None,
            created_at=None,
            updated_at=None,
            last_played_at=None,
            release_date=None
        )
        
        assert song.album_id is None
        assert song.artist_id is None
        assert song.album_title is None
        assert song.artist_name is None
        assert song.track_number is None
        assert song.file_url is None
        assert song.thumbnail_url is None
        assert song.lyrics is None
        assert song.source_id is None
        assert song.source_url is None
        assert song.created_at is None
        assert song.updated_at is None
        assert song.last_played_at is None
        assert song.release_date is None
        
    def test_song_entity_type_validation(self):
        """Test validación de tipos"""
        song = SongEntity(
            id="song-types",
            title="Type Test Song",
            genre_ids=["rock", "pop"],
            duration_seconds=180,
            track_number=3,
            play_count=500,
            favorite_count=100,
            download_count=25
        )
        
        assert isinstance(song.id, str)
        assert isinstance(song.title, str)
        assert isinstance(song.genre_ids, list)
        assert isinstance(song.duration_seconds, int)
        assert isinstance(song.track_number, int)
        assert isinstance(song.play_count, int)
        assert isinstance(song.favorite_count, int)
        assert isinstance(song.download_count, int)
        assert isinstance(song.source_type, str)
        assert isinstance(song.audio_quality, str)
        
    def test_song_entity_edge_cases(self):
        """Test casos límite"""
        # Canción con título muy largo
        long_title = "A" * 500
        song_long_title = SongEntity(
            id="song-long-title",
            title=long_title
        )
        assert song_long_title.title == long_title
        
        # Canción con duración cero
        zero_duration_song = SongEntity(
            id="song-zero-duration",
            title="Zero Duration Song",
            duration_seconds=0
        )
        assert zero_duration_song.duration_seconds == 0
        
        # Canción con muchos géneros
        many_genres = [f"genre-{i}" for i in range(20)]
        multi_genre_song = SongEntity(
            id="song-many-genres",
            title="Multi Genre Song",
            genre_ids=many_genres
        )
        assert len(multi_genre_song.genre_ids) == 20
        
    def test_song_entity_empty_values(self):
        """Test valores vacíos"""
        song = SongEntity(
            id="song-empty",
            title="",  # título vacío
            genre_ids=[],  # lista vacía
            lyrics="",  # lyrics vacías
            album_title="",
            artist_name=""
        )
        
        assert song.title == ""
        assert song.genre_ids == []
        assert song.lyrics == ""
        assert song.album_title == ""
        assert song.artist_name == ""
