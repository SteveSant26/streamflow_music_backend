"""
Tests para las entidades del dominio de playlists
"""

import pytest
from datetime import datetime
from apps.playlists.domain.entities import PlaylistEntity, PlaylistSongEntity


class TestPlaylistEntity:
    """Tests para la entidad PlaylistEntity"""

    def test_playlist_entity_creation_minimal(self):
        """Test creación de playlist con datos mínimos"""
        playlist = PlaylistEntity(
            id="playlist-1",
            name="Mi Playlist",
            description=None,
            user_id="user-123",
            is_default=False,
            is_public=True,
            created_at=datetime.now()
        )
        
        assert playlist.id == "playlist-1"
        assert playlist.name == "Mi Playlist"
        assert playlist.description is None
        assert playlist.user_id == "user-123"
        assert playlist.is_default is False
        assert playlist.is_public is True
        assert playlist.playlist_img is None
        assert playlist.updated_at is None
        assert playlist.songs is None

    def test_playlist_entity_creation_complete(self):
        """Test creación de playlist con datos completos"""
        songs = [
            PlaylistSongEntity(
                id="ps-1",
                playlist_id="playlist-1",
                song_id="song-1",
                position=0,
                added_at=datetime.now()
            )
        ]
        
        playlist = PlaylistEntity(
            id="playlist-1",
            name="Mi Playlist Completa",
            description="Una playlist de prueba",
            user_id="user-123",
            is_default=True,
            is_public=False,
            created_at=datetime.now(),
            playlist_img="https://example.com/image.jpg",
            updated_at=datetime.now(),
            songs=songs
        )
        
        assert playlist.id == "playlist-1"
        assert playlist.name == "Mi Playlist Completa"
        assert playlist.description == "Una playlist de prueba"
        assert playlist.user_id == "user-123"
        assert playlist.is_default is True
        assert playlist.is_public is False
        assert playlist.playlist_img == "https://example.com/image.jpg"
        assert playlist.updated_at is not None
        assert len(playlist.songs) == 1

    def test_playlist_entity_song_count_property(self):
        """Test propiedad song_count"""
        # Sin canciones
        playlist = PlaylistEntity(
            id="playlist-1",
            name="Playlist Vacía",
            description=None,
            user_id="user-123",
            is_default=False,
            is_public=True,
            created_at=datetime.now()
        )
        
        assert playlist.song_count == 0
        
        # Con canciones
        songs = [
            PlaylistSongEntity(
                id="ps-1",
                playlist_id="playlist-1",
                song_id="song-1",
                position=0,
                added_at=datetime.now()
            ),
            PlaylistSongEntity(
                id="ps-2",
                playlist_id="playlist-1",
                song_id="song-2",
                position=1,
                added_at=datetime.now()
            )
        ]
        
        playlist.songs = songs
        assert playlist.song_count == 2

    def test_playlist_entity_name_validation_empty(self):
        """Test validación de nombre vacío"""
        with pytest.raises(ValueError, match="El nombre de la playlist no puede estar vacío"):
            PlaylistEntity(
                id="playlist-1",
                name="",
                description=None,
                user_id="user-123",
                is_default=False,
                is_public=True,
                created_at=datetime.now()
            )

    def test_playlist_entity_name_validation_whitespace(self):
        """Test validación de nombre solo espacios"""
        with pytest.raises(ValueError, match="El nombre de la playlist no puede estar vacío"):
            PlaylistEntity(
                id="playlist-1",
                name="   ",
                description=None,
                user_id="user-123",
                is_default=False,
                is_public=True,
                created_at=datetime.now()
            )

    def test_playlist_entity_name_validation_too_long(self):
        """Test validación de nombre muy largo"""
        long_name = "a" * 256
        
        with pytest.raises(ValueError, match="El nombre de la playlist no puede exceder 255 caracteres"):
            PlaylistEntity(
                id="playlist-1",
                name=long_name,
                description=None,
                user_id="user-123",
                is_default=False,
                is_public=True,
                created_at=datetime.now()
            )

    def test_playlist_entity_name_validation_max_length(self):
        """Test nombre con longitud máxima válida"""
        max_length_name = "a" * 255
        
        playlist = PlaylistEntity(
            id="playlist-1",
            name=max_length_name,
            description=None,
            user_id="user-123",
            is_default=False,
            is_public=True,
            created_at=datetime.now()
        )
        
        assert playlist.name == max_length_name
        assert len(playlist.name) == 255

    def test_playlist_entity_default_playlist_behavior(self):
        """Test comportamiento de playlist por defecto"""
        default_playlist = PlaylistEntity(
            id="favorites-1",
            name="Favoritos",
            description="Playlist de canciones favoritas",
            user_id="user-123",
            is_default=True,
            is_public=False,
            created_at=datetime.now()
        )
        
        assert default_playlist.is_default is True
        assert default_playlist.name == "Favoritos"

    def test_playlist_entity_public_private_playlists(self):
        """Test playlists públicas y privadas"""
        public_playlist = PlaylistEntity(
            id="playlist-public",
            name="Playlist Pública",
            description=None,
            user_id="user-123",
            is_default=False,
            is_public=True,
            created_at=datetime.now()
        )
        
        private_playlist = PlaylistEntity(
            id="playlist-private",
            name="Playlist Privada",
            description=None,
            user_id="user-123",
            is_default=False,
            is_public=False,
            created_at=datetime.now()
        )
        
        assert public_playlist.is_public is True
        assert private_playlist.is_public is False


class TestPlaylistSongEntity:
    """Tests para la entidad PlaylistSongEntity"""

    def test_playlist_song_entity_creation(self):
        """Test creación de PlaylistSongEntity"""
        added_time = datetime.now()
        
        playlist_song = PlaylistSongEntity(
            id="ps-1",
            playlist_id="playlist-1",
            song_id="song-1",
            position=0,
            added_at=added_time
        )
        
        assert playlist_song.id == "ps-1"
        assert playlist_song.playlist_id == "playlist-1"
        assert playlist_song.song_id == "song-1"
        assert playlist_song.position == 0
        assert playlist_song.added_at == added_time

    def test_playlist_song_entity_position_validation_negative(self):
        """Test validación de posición negativa"""
        with pytest.raises(ValueError, match="La posición debe ser un número positivo"):
            PlaylistSongEntity(
                id="ps-1",
                playlist_id="playlist-1",
                song_id="song-1",
                position=-1,
                added_at=datetime.now()
            )

    def test_playlist_song_entity_position_validation_zero(self):
        """Test validación de posición cero (válida)"""
        playlist_song = PlaylistSongEntity(
            id="ps-1",
            playlist_id="playlist-1",
            song_id="song-1",
            position=0,
            added_at=datetime.now()
        )
        
        assert playlist_song.position == 0

    def test_playlist_song_entity_position_validation_positive(self):
        """Test validación de posición positiva"""
        playlist_song = PlaylistSongEntity(
            id="ps-1",
            playlist_id="playlist-1",
            song_id="song-1",
            position=10,
            added_at=datetime.now()
        )
        
        assert playlist_song.position == 10

    def test_playlist_song_entity_multiple_positions(self):
        """Test múltiples canciones con diferentes posiciones"""
        songs = []
        
        for i in range(5):
            song = PlaylistSongEntity(
                id=f"ps-{i}",
                playlist_id="playlist-1",
                song_id=f"song-{i}",
                position=i,
                added_at=datetime.now()
            )
            songs.append(song)
        
        assert len(songs) == 5
        for i, song in enumerate(songs):
            assert song.position == i
            assert song.song_id == f"song-{i}"
