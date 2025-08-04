import uuid

from django.db import models


class PlaylistSongModel(models.Model):
    """Modelo intermedio para las canciones en playlists"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    playlist = models.ForeignKey(
        "playlists.PlaylistModel",
        on_delete=models.CASCADE,
        related_name="songs",
        help_text="Playlist que contiene la canción"
    )
    song = models.ForeignKey(
        "songs.SongModel",
        on_delete=models.CASCADE,
        related_name="playlist_entries",
        help_text="Canción en la playlist"
    )
    
    # Posición de la canción en la playlist
    position = models.PositiveIntegerField(
        help_text="Posición de la canción en la playlist (empezando desde 1)"
    )
    
    # Metadatos
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = "playlists"
        db_table = "playlist_songs"
        ordering = ["playlist", "position"]
        verbose_name = "Canción en Playlist"
        verbose_name_plural = "Canciones en Playlists"
        indexes = [
            models.Index(fields=["playlist", "position"]),
            models.Index(fields=["song"]),
        ]
        constraints = [
            # Una canción no puede estar dos veces en la misma playlist
            models.UniqueConstraint(
                fields=["playlist", "song"],
                name="unique_song_per_playlist"
            ),
            # La posición debe ser única por playlist
            models.UniqueConstraint(
                fields=["playlist", "position"],
                name="unique_position_per_playlist"
            )
        ]
    
    def __str__(self):
        return f"{self.playlist.name} - {self.song.title} (pos: {self.position})"
    
    def save(self, *args, **kwargs):
        """Override save para validaciones adicionales"""
        if self.position <= 0:
            raise ValueError("La posición debe ser un número positivo")
        
        super().save(*args, **kwargs)
