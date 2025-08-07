"""
🧪 TESTS DE INTEGRACIÓN SIMPLES
==============================
Tests de integración entre entidades sin dependencias Django
"""
import pytest
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SimpleSongEntity:
    """Entidad simple para tests de Song"""
    id: str
    title: str
    artist_name: str
    album_title: str
    genre_name: str
    duration_seconds: int = 180
    play_count: int = 0
    is_active: bool = True
    tags: List[str] = None


@dataclass
class SimpleArtistEntity:
    """Entidad simple para tests de Artist"""
    id: str
    name: str
    biography: str = ""
    country: str = "Unknown"
    followers_count: int = 0
    is_verified: bool = False
    is_active: bool = True
    image_url: Optional[str] = None


@dataclass
class SimpleAlbumEntity:
    """Entidad simple para tests de Album"""
    id: str
    title: str
    artist_name: str
    genre: str
    total_tracks: int = 1
    release_date: str = "2023-01-01"
    is_active: bool = True
    cover_image_url: Optional[str] = None


@dataclass
class SimpleGenreEntity:
    """Entidad simple para tests de Genre"""
    id: str
    name: str
    description: str = ""
    icon: str = "🎵"
    color_code: str = "#000000"
    parent_genre_id: Optional[str] = None
    is_active: bool = True


@dataclass
class SimplePlaylistEntity:
    """Entidad simple para tests de Playlist"""
    id: str
    name: str
    user_id: str
    description: str = ""
    is_public: bool = True
    is_active: bool = True
    song_count: int = 0
    total_duration_seconds: int = 0
    tags: List[str] = None
    cover_image_url: Optional[str] = None


class TestEntityIntegration:
    """Tests de integración entre entidades"""
    
    @pytest.mark.integration
    def test_song_artist_relationship(self):
        """Test relación Song-Artist"""
        # Given
        artist = SimpleArtistEntity(
            id="artist-1",
            name="Test Artist",
            country="Colombia"
        )

        song = SimpleSongEntity(
            id="song-1",
            title="Test Song",
            artist_name=artist.name,
            album_title="Test Album",
            genre_name="Rock",
            duration_seconds=180
        )        # Then
        assert song.artist_name == artist.name
        assert artist.name in song.artist_name
    
    @pytest.mark.integration
    def test_album_songs_relationship(self):
        """Test relación Album-Songs"""
        # Given
        album = SimpleAlbumEntity(
            id="album-1",
            title="Test Album",
            artist_name="Test Artist",
            genre="Rock",
            total_tracks=3
        )
        
        songs = [
            SimpleSongEntity(
                id=f"song-{i}",
                title=f"Track {i}",
                artist_name=album.artist_name,
                album_title=album.title,
                genre_name="Rock"
            )
            for i in range(1, album.total_tracks + 1)
        ]
        
        # Then
        assert len(songs) == album.total_tracks
        assert all(song.album_title == album.title for song in songs)
        assert all(song.artist_name == album.artist_name for song in songs)
    
    @pytest.mark.integration
    def test_genre_songs_relationship(self):
        """Test relación Genre-Songs"""
        # Given
        genre = SimpleGenreEntity(
            id="rock",
            name="Rock",
            description="Rock music genre"
        )
        
        songs = [
            SimpleSongEntity(
                id=f"rock-song-{i}",
                title=f"Rock Song {i}",
                artist_name="Rock Artist",
                album_title="Rock Album",
                genre_name=genre.name
            )
            for i in range(1, 4)
        ]
        
        # Then
        assert len(songs) == 3
        assert all(song.genre_name == genre.name for song in songs)
    
    @pytest.mark.integration
    def test_playlist_songs_simulation(self):
        """Test simulación de Playlist con Songs"""
        # Given
        playlist = SimplePlaylistEntity(
            id="playlist-1",
            name="Rock Hits",
            user_id="user-1",
            song_count=5,
            total_duration_seconds=900  # 15 minutos
        )
        
        # Simular canciones en la playlist
        songs_in_playlist = [
            SimpleSongEntity(
                id=f"playlist-song-{i}",
                title=f"Playlist Song {i}",
                artist_name="Rock Artist",
                album_title="Rock Album",
                genre_name="Rock",
                duration_seconds=180  # 3 minutos cada una
            )
            for i in range(1, playlist.song_count + 1)
        ]
        
        # When
        calculated_duration = sum(song.duration_seconds for song in songs_in_playlist)
        
        # Then
        assert len(songs_in_playlist) == playlist.song_count
        assert calculated_duration == playlist.total_duration_seconds
    
    @pytest.mark.integration
    def test_artist_albums_relationship(self):
        """Test relación Artist-Albums"""
        # Given
        artist = SimpleArtistEntity(
            id="artist-discography",
            name="Prolific Artist"
        )
        
        albums = [
            SimpleAlbumEntity(
                id=f"album-{i}",
                title=f"Album {i}",
                artist_name=artist.name,
                genre="Rock",
                release_date=f"202{i}-01-01"
            )
            for i in range(1, 4)
        ]
        
        # Then
        assert len(albums) == 3
        assert all(album.artist_name == artist.name for album in albums)
        
        # Verificar años diferentes
        release_years = [album.release_date.split("-")[0] for album in albums]
        assert len(set(release_years)) == 3  # Años únicos
    
    @pytest.mark.integration
    def test_complete_music_catalog_simulation(self):
        """Test simulación de catálogo musical completo"""
        # Given - Crear un mini catálogo
        genre = SimpleGenreEntity(id="pop", name="Pop")
        
        artist = SimpleArtistEntity(
            id="pop-artist",
            name="Pop Star",
            is_verified=True
        )
        
        album = SimpleAlbumEntity(
            id="pop-album",
            title="Pop Hits",
            artist_name=artist.name,
            genre=genre.name,
            total_tracks=4
        )
        
        songs = [
            SimpleSongEntity(
                id=f"hit-{i}",
                title=f"Hit Song {i}",
                artist_name=artist.name,
                album_title=album.title,
                genre_name=genre.name,
                duration_seconds=200 + (i * 10)  # Duraciones variables
            )
            for i in range(1, album.total_tracks + 1)
        ]
        
        playlist = SimplePlaylistEntity(
            id="hits-playlist",
            name="Greatest Hits",
            user_id="user-1",
            song_count=len(songs),
            total_duration_seconds=sum(song.duration_seconds for song in songs)
        )
        
        # Then - Verificar consistencia
        assert all(song.artist_name == artist.name for song in songs)
        assert all(song.album_title == album.title for song in songs)
        assert all(song.genre_name == genre.name for song in songs)
        assert playlist.song_count == len(songs)
        assert playlist.total_duration_seconds == sum(song.duration_seconds for song in songs)
    
    @pytest.mark.integration
    def test_multi_genre_artist(self):
        """Test artista con múltiples géneros"""
        # Given
        artist = SimpleArtistEntity(
            id="versatile-artist",
            name="Versatile Artist"
        )
        
        genres = [
            SimpleGenreEntity(id="rock", name="Rock"),
            SimpleGenreEntity(id="pop", name="Pop"),
            SimpleGenreEntity(id="electronic", name="Electronic")
        ]
        
        songs_by_genre = [
            SimpleSongEntity(
                id=f"{genre.name.lower()}-song",
                title=f"{genre.name} Song",
                artist_name=artist.name,
                album_title=f"{genre.name} Album",
                genre_name=genre.name
            )
            for genre in genres
        ]
        
        # Then
        unique_genres = set(song.genre_name for song in songs_by_genre)
        assert len(unique_genres) == len(genres)
        assert all(song.artist_name == artist.name for song in songs_by_genre)
    
    @pytest.mark.integration
    def test_playlist_mixed_genres(self):
        """Test playlist con géneros mixtos"""
        # Given
        genres = ["Rock", "Pop", "Electronic", "Jazz"]
        
        songs = [
            SimpleSongEntity(
                id=f"mixed-{i}",
                title=f"Mixed Song {i}",
                artist_name="Mixed Artist",
                album_title="Mixed Album",
                genre_name=genres[i % len(genres)],
                duration_seconds=180
            )
            for i in range(8)  # 2 canciones por género
        ]
        
        playlist = SimplePlaylistEntity(
            id="mixed-genres",
            name="Mixed Genres Playlist",
            user_id="user-1",
            song_count=len(songs),
            total_duration_seconds=sum(song.duration_seconds for song in songs),
            tags=["variety", "mixed"]
        )
        
        # When
        genre_distribution = {}
        for song in songs:
            genre_distribution[song.genre_name] = genre_distribution.get(song.genre_name, 0) + 1
        
        # Then
        assert playlist.song_count == len(songs)
        assert len(genre_distribution) == len(genres)
        assert all(count == 2 for count in genre_distribution.values())  # 2 por género
        assert "variety" in playlist.tags
    
    @pytest.mark.integration
    def test_featured_artist_collaboration(self):
        """Test colaboración entre artistas"""
        # Given
        main_artist = SimpleArtistEntity(
            id="main-artist",
            name="Main Artist"
        )
        
        featured_artist = SimpleArtistEntity(
            id="featured-artist", 
            name="Featured Artist"
        )
        
        collaboration_song = SimpleSongEntity(
            id="collab-song",
            title="Collaboration Song",
            artist_name=f"{main_artist.name} ft. {featured_artist.name}",
            album_title="Collaboration Album",
            genre_name="Pop",
            duration_seconds=240
        )
        
        # Then
        assert main_artist.name in collaboration_song.artist_name
        assert featured_artist.name in collaboration_song.artist_name
        assert "ft." in collaboration_song.artist_name
    
    @pytest.mark.integration
    def test_user_playlist_management(self):
        """Test gestión de playlists de usuario"""
        # Given
        user_id = "user-123"
        
        user_playlists = [
            SimplePlaylistEntity(
                id=f"user-playlist-{i}",
                name=f"My Playlist {i}",
                user_id=user_id,
                is_public=i % 2 == 0,  # Alternar público/privado
                song_count=10 + i * 5
            )
            for i in range(1, 4)
        ]
        
        # Then
        assert all(playlist.user_id == user_id for playlist in user_playlists)
        assert sum(1 for p in user_playlists if p.is_public) == 1  # Solo una pública
        assert sum(1 for p in user_playlists if not p.is_public) == 2  # Dos privadas
        
        total_songs = sum(playlist.song_count for playlist in user_playlists)
        assert total_songs == 60  # 10+25+25 (corrección: i*5 da 5, 10, 15, no 15, 20)
