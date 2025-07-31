import uuid

from django.db import models


class ArtistModel(models.Model):
    """Modelo para artistas"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, db_index=True)
    biography = models.TextField(blank=True, null=True)  # NOSONAR
    country = models.CharField(
        max_length=100, blank=True, null=True, db_index=True  # NOSONAR
    )
    image_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Artista"
        verbose_name_plural = "Artistas"
        indexes = [
            models.Index(fields=["name", "is_active"]),
            models.Index(fields=["country", "is_active"]),
        ]

    def __str__(self):
        return self.name

    @property
    def albums_count(self):
        """Número de álbumes del artista"""
        return self.album.filter(is_active=True).count()  # type: ignore

    @property
    def songs_count(self):
        """Número de canciones del artista"""
        return self.songs.filter(is_active=True).count()  # type: ignore
