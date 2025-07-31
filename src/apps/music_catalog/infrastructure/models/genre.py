import uuid

from django.db import models


class GenreModel(models.Model):
    """Modelo para géneros musicales"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Género"
        verbose_name_plural = "Géneros"

    def __str__(self):
        return self.name
