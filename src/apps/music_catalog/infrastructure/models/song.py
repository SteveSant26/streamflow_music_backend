from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Song(models.Model):
    """Modelo para canciones"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, db_index=True)
    artist = models.ForeignKey(
        'Artist', 
        on_delete=models.CASCADE, 
        related_name='songs',
        db_index=True
    )
    album = models.ForeignKey(
        'Album', 
        on_delete=models.CASCADE, 
        related_name='songs',
        blank=True, 
        null=True,
        db_index=True
    )
    duration_seconds = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7200)]  # Max 2 horas
    )
    file_url = models.URLField(blank=True, null=True)
    lyrics = models.TextField(blank=True, null=True)
    track_number = models.PositiveIntegerField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(200)]
    )
    genre = models.ForeignKey(
        'Genre', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='songs',
        db_index=True
    )
    play_count = models.PositiveIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['album', 'track_number', 'title']
        verbose_name = 'Canción'
        verbose_name_plural = 'Canciones'
        indexes = [
            models.Index(fields=['artist', 'is_active']),
            models.Index(fields=['album', 'track_number']),
            models.Index(fields=['genre', 'is_active']),
            models.Index(fields=['title', 'is_active']),
            models.Index(fields=['-play_count', 'is_active']),  # Para canciones populares
        ]
        unique_together = [
            ['title', 'artist', 'album'],  # No duplicar canciones en mismo álbum
            ['album', 'track_number'],      # No duplicar número de pista en álbum
        ]
    
    def __str__(self):
        if self.album:
            return f"{self.title} - {self.artist.name} ({self.album.title})"
        return f"{self.title} - {self.artist.name}"
    
    @property
    def duration_formatted(self):
        """Duración formateada como MM:SS"""
        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60
        return f"{minutes}:{seconds:02d}"
    
    def increment_play_count(self):
        """Incrementa el contador de reproducciones"""
        self.play_count += 1
        self.save(update_fields=['play_count'])
    
    def save(self, *args, **kwargs):
        """Override save para mantener consistencia de datos"""
        # Si tiene álbum, debe ser del mismo artista
        if self.album and self.album.artist != self.artist:
            raise ValueError("El álbum debe pertenecer al mismo artista")
        
        # Si tiene álbum pero no género, usar el género del álbum
        if self.album and not self.genre and self.album.genre:
            self.genre = self.album.genre
        
        super().save(*args, **kwargs)
        
        # Actualizar estadísticas del álbum si existe
        if self.album:
            self.album.update_album_stats()
