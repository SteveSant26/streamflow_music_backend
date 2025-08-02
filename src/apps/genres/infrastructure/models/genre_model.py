from django.db import models


class GenreModel(models.Model):
    """Modelo Django para Género Musical"""

    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField(
        max_length=100, unique=True, verbose_name="Nombre del género"
    )
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    image_url = models.URLField(blank=True, null=True, verbose_name="URL de imagen")
    color_hex = models.CharField(
        max_length=7,
        blank=True,
        null=True,  # NOSONAR
        verbose_name="Color representativo",
        help_text="Color en formato hexadecimal (#RRGGBB)",
    )
    popularity_score = models.PositiveIntegerField(
        default=0, verbose_name="Puntuación de popularidad"
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        db_table = "genres"
        verbose_name = "Género Musical"
        verbose_name_plural = "Géneros Musicales"
        ordering = ["-popularity_score", "name"]

    def __str__(self):
        return self.name
