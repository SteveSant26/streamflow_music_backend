from django.db import models


class AlbumModel(models.Model):
    """Modelo Django para Álbum"""

    id = models.UUIDField(primary_key=True, editable=False)
    title = models.CharField(max_length=300, verbose_name="Título del álbum")
    artist_id = models.UUIDField(verbose_name="ID del artista")
    artist_name = models.CharField(
        max_length=200,
        verbose_name="Nombre del artista",
        help_text="Desnormalizado para rendimiento",
    )
    release_date = models.DateField(
        blank=True, null=True, verbose_name="Fecha de lanzamiento"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    cover_image_url = models.URLField(
        blank=True, null=True, verbose_name="URL de portada"
    )
    total_tracks = models.PositiveIntegerField(
        default=0, verbose_name="Total de pistas"
    )
    play_count = models.PositiveBigIntegerField(
        default=0, verbose_name="Reproducciones"
    )

    # TODO: Uncomment after running migration 0002_add_source_fields.py
    # # Metadatos de origen
    # source_type = models.CharField(
    #     max_length=20,
    #     default="manual",
    #     choices=[
    #         ("manual", "Manual"),
    #         ("youtube", "YouTube"),
    #         ("spotify", "Spotify"),
    #         ("soundcloud", "SoundCloud"),
    #     ],
    #     verbose_name="Tipo de fuente"
    # )
    # source_id = models.CharField(
    #     max_length=100, blank=True, null=True, db_index=True,
    #     verbose_name="ID de fuente externa"
    # )
    # source_url = models.URLField(
    #     blank=True, null=True, verbose_name="URL de fuente externa"
    # )

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        db_table = "albums"
        verbose_name = "Álbum"
        verbose_name_plural = "Álbumes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["artist_id"]),
            models.Index(fields=["release_date"]),
            models.Index(fields=["play_count"]),
            # TODO: Uncomment after migration 0002_add_source_fields.py
            # models.Index(fields=["source_type", "source_id"]),
        ]
        # TODO: Uncomment after migration 0002_add_source_fields.py
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["source_type", "source_id"],
        #         condition=models.Q(source_id__isnull=False),
        #         name="unique_album_source_per_type",
        #     ),
        # ]

    async def increase_play_count(self):
        """Incrementa el contador de reproducciones del álbum"""
        self.play_count += 1
        await self.asave(update_fields=["play_count"])

    def __str__(self):
        return f"{self.title} - {self.artist_name}"
