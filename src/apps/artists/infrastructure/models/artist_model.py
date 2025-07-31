from django.db import models


class ArtistModel(models.Model):
    """Modelo Django para Artista"""

    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nombre del artista")
    biography = models.TextField(blank=True, null=True, verbose_name="Biografía")
    country = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="País"
    )
    image_url = models.URLField(blank=True, null=True, verbose_name="URL de imagen")
    followers_count = models.PositiveIntegerField(
        default=0, verbose_name="Cantidad de seguidores"
    )
    is_verified = models.BooleanField(default=False, verbose_name="Verificado")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        db_table = "artists"
        verbose_name = "Artista"
        verbose_name_plural = "Artistas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["country"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["followers_count"]),
        ]

    def __str__(self):
        return self.name
