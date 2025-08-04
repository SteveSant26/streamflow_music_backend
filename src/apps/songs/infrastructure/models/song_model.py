import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class SongModel(models.Model):
    """Modelo de canción en la aplicación de música"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Información básica
    title = models.CharField(max_length=255)

    # Relaciones
    album_id = models.UUIDField(null=True, blank=True, db_index=True)
    artist_id = models.UUIDField(null=True, blank=True, db_index=True)

    # Relación con géneros - Many to Many para permitir múltiples géneros por canción
    genres = models.ManyToManyField(
        "genres.GenreModel",
        blank=True,
        related_name="songs",
        help_text="Géneros musicales asociados a esta canción",
    )

    # Información desnormalizada para mejor rendimiento en consultas
    album_title = models.CharField(
        max_length=255, null=True, blank=True, db_index=True  # NOSONAR
    )  # NOSONAR

    # Metadatos de la canción
    duration_seconds = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(86400)],  # Máximo 24 horas
    )
    track_number = models.PositiveIntegerField(null=True, blank=True)

    # URLs y archivos almacenados en Supabase
    file_url = models.URLField(null=True, blank=True, max_length=500)
    thumbnail_url = models.URLField(null=True, blank=True, max_length=500)

    # Contenido adicional
    lyrics = models.TextField(null=True, blank=True)  # NOSONAR

    # Métricas internas de la aplicación
    play_count = models.PositiveIntegerField(default=0, db_index=True)
    favorite_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    # Metadatos de origen (para saber de dónde vino la canción)
    source_type = models.CharField(
        max_length=20,
        default="youtube",
        choices=[
            ("youtube", "YouTube"),
            ("upload", "Subida directa"),
            ("spotify", "Spotify"),
            ("soundcloud", "SoundCloud"),
        ],
    )
    source_id = models.CharField(
        max_length=100, null=True, blank=True, db_index=True  # noqa
    )  # NOSONAR
    source_url = models.URLField(null=True, blank=True, max_length=500)

    # Estados y configuración
    audio_quality = models.CharField(
        max_length=20,
        default="standard",
        choices=[
            ("standard", "Estándar (128kbps)"),
            ("high", "Alta (320kbps)"),
            ("lossless", "Sin pérdida (FLAC)"),
        ],
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_played_at = models.DateTimeField(null=True, blank=True)
    release_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "songs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["source_type", "source_id"]),
            models.Index(fields=["album_title", "track_number"]),
            models.Index(fields=["play_count"], name="songs_most_played_idx"),
            models.Index(fields=["favorite_count"], name="songs_most_favorited_idx"),
            models.Index(fields=["last_played_at"], name="songs_recently_played_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["source_type", "source_id"],
                condition=models.Q(source_id__isnull=False),
                name="unique_source_per_type",
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def duration_formatted(self) -> str:
        """Retorna la duración en formato MM:SS"""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    async def increment_play_count(self):
        """Incrementa el contador de reproducciones y actualiza last_played_at"""
        from django.utils import timezone

        self.play_count += 1
        self.last_played_at = timezone.now()
        await self.asave(update_fields=["play_count", "last_played_at"])

    async def increment_favorite_count(self):
        """Incrementa el contador de favoritos"""
        self.favorite_count += 1
        await self.asave(update_fields=["favorite_count"])

    async def increment_download_count(self):
        """Incrementa el contador de descargas"""
        self.download_count += 1
        await self.asave(update_fields=["download_count"])

    async def get_primary_genre(self):
        """Retorna el primer género asignado como género principal"""
        return await self.genres.afirst()
