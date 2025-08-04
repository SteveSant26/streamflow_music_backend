import uuid

from django.db import models


class PlaylistModel(models.Model):
    """Modelo de playlist en la aplicación de música"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Relación con el usuario
    user = models.ForeignKey(
        "user_profile.UserProfileModel",
        on_delete=models.CASCADE,
        related_name="playlists",
        help_text="Usuario propietario de la playlist"
    )
    
    # Configuraciones de la playlist
    is_default = models.BooleanField(
        default=False,
        help_text="Indica si es una playlist por defecto (como 'Favoritos') que no se puede eliminar"
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Indica si la playlist es pública o privada"
    )
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = "playlists"
        db_table = "playlists"
        ordering = ["created_at"]
        verbose_name = "Playlist"
        verbose_name_plural = "Playlists"
        indexes = [
            models.Index(fields=["user", "is_default"]),
            models.Index(fields=["user", "created_at"]),
        ]
        constraints = [
            # Un usuario solo puede tener una playlist por defecto con el mismo nombre
            models.UniqueConstraint(
                fields=["user", "name"],
                condition=models.Q(is_default=True),
                name="unique_default_playlist_per_user"
            )
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"
    
    @property
    def total_songs(self):
        """Retorna el número total de canciones en la playlist"""
        return self.songs.count()
    
    def save(self, *args, **kwargs):
        """Override save para validaciones adicionales"""
        # Validar que el nombre no esté vacío
        if not self.name or not self.name.strip():
            raise ValueError("El nombre de la playlist no puede estar vacío")
        
        super().save(*args, **kwargs)
