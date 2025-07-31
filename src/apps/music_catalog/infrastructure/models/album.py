import uuid

from django.db import models


class AlbumModel(models.Model):
    """Modelo para álbumes"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, db_index=True)
    artist = models.ForeignKey(
        "Artist", on_delete=models.CASCADE, related_name="albums", db_index=True
    )
    release_date = models.DateField(blank=True, null=True, db_index=True)
    cover_image_url = models.URLField(blank=True, null=True)
    total_tracks = models.PositiveIntegerField(default=0)
    duration_seconds = models.PositiveIntegerField(default=0)
    genre = models.ForeignKey(
        "Genre",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="albums",
        db_index=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-release_date", "title"]
        verbose_name = "Álbum"
        verbose_name_plural = "Álbumes"
        indexes = [
            models.Index(fields=["artist", "release_date"]),
            models.Index(fields=["genre", "is_active"]),
            models.Index(fields=["title", "is_active"]),
        ]
        unique_together = ["title", "artist"]

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    @property
    def songs_count(self):
        """Número de canciones en el álbum"""
        return self.songs.filter(is_active=True).count()  # type: ignore

    def update_album_stats(self):
        """Actualiza estadísticas del álbum basado en sus canciones"""
        songs = self.songs.filter(is_active=True)  # type: ignore
        self.total_tracks = songs.count()
        self.duration_seconds = sum(song.duration_seconds for song in songs)
        self.save(update_fields=["total_tracks", "duration_seconds"])
