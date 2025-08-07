import uuid
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class FavoriteSongModel(models.Model):
    """Modelo para canciones favoritas de usuarios"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_songs",
        help_text="Usuario que marcó la canción como favorita"
    )
    song = models.ForeignKey(
        "songs.SongModel",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        help_text="Canción marcada como favorita"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "favorite_songs"
        unique_together = ["user", "song"]  # Un usuario no puede marcar la misma canción como favorita dos veces
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["song", "-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.song.title}"


class FavoriteArtistModel(models.Model):
    """Modelo para artistas favoritos de usuarios"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_artists",
        help_text="Usuario que marcó el artista como favorito"
    )
    artist = models.ForeignKey(
        "artists.ArtistModel",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        help_text="Artista marcado como favorito"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "favorite_artists"
        unique_together = ["user", "artist"]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["artist", "-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.artist.name}"


class FavoriteAlbumModel(models.Model):
    """Modelo para álbumes favoritos de usuarios"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorite_albums",
        help_text="Usuario que marcó el álbum como favorito"
    )
    album = models.ForeignKey(
        "albums.AlbumModel",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        help_text="Álbum marcado como favorito"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "favorite_albums"
        unique_together = ["user", "album"]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["album", "-created_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.album.title}"
