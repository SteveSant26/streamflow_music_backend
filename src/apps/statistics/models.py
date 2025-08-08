import uuid
from django.db import models
from django.utils import timezone


class StatisticsModel(models.Model):
    """Modelo proxy para las estadísticas - no crea tabla nueva"""
    
    class Meta:
        managed = False  # No crear tabla en la BD
        verbose_name = "Estadística"
        verbose_name_plural = "Estadísticas"


class UserPlayHistoryModel(models.Model):
    """Historial de reproducciones por usuario"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    user = models.ForeignKey(
        "user_profile.UserProfileModel",
        on_delete=models.CASCADE,
        related_name="play_history",
        help_text="Usuario que reprodujo la canción"
    )
    song = models.ForeignKey(
        "songs.SongModel",
        on_delete=models.CASCADE,
        related_name="play_history",
        help_text="Canción reproducida"
    )
    
    # Metadatos de reproducción
    played_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Fecha y hora de reproducción"
    )
    duration_played = models.PositiveIntegerField(
        help_text="Duración reproducida en segundos"
    )
    completed = models.BooleanField(
        default=False,
        help_text="Si la canción se reprodujo completamente"
    )
    
    # Contexto de reproducción
    source = models.CharField(
        max_length=50,
        choices=[
            ('playlist', 'Playlist'),
            ('album', 'Álbum'),
            ('search', 'Búsqueda'),
            ('recommendation', 'Recomendación'),
            ('shuffle', 'Aleatorio'),
            ('direct', 'Directo'),
        ],
        default='direct',
        help_text="Fuente de la reproducción"
    )
    
    # Metadatos adicionales
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('web', 'Web'),
            ('mobile', 'Móvil'),
            ('desktop', 'Escritorio'),
            ('tablet', 'Tablet'),
        ],
        default='web',
        help_text="Tipo de dispositivo usado"
    )
    
    class Meta:
        db_table = "user_play_history"
        verbose_name = "Historial de Reproducción"
        verbose_name_plural = "Historial de Reproducciones"
        ordering = ["-played_at"]
        indexes = [
            models.Index(fields=["user", "played_at"]),
            models.Index(fields=["song", "played_at"]),
            models.Index(fields=["played_at"]),
            models.Index(fields=["user", "song"]),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.song.title} ({self.played_at})"


class UserFavoriteArtistModel(models.Model):
    """Artistas favoritos por usuario"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    user = models.ForeignKey(
        "user_profile.UserProfileModel",
        on_delete=models.CASCADE,
        related_name="favorite_artists",
        help_text="Usuario"
    )
    artist = models.ForeignKey(
        "artists.ArtistModel",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        help_text="Artista favorito"
    )
    
    # Metadatos
    added_at = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha cuando se agregó a favoritos"
    )
    
    class Meta:
        db_table = "user_favorite_artists"
        verbose_name = "Artista Favorito"
        verbose_name_plural = "Artistas Favoritos"
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "artist"],
                name="unique_user_favorite_artist"
            )
        ]
        indexes = [
            models.Index(fields=["user", "added_at"]),
            models.Index(fields=["artist", "added_at"]),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.artist.name}"


class UserFavoriteSongModel(models.Model):
    """Canciones favoritas por usuario"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    user = models.ForeignKey(
        "user_profile.UserProfileModel",
        on_delete=models.CASCADE,
        related_name="favorite_songs",
        help_text="Usuario"
    )
    song = models.ForeignKey(
        "songs.SongModel",
        on_delete=models.CASCADE,
        related_name="favorited_by",
        help_text="Canción favorita"
    )
    
    # Metadatos
    added_at = models.DateTimeField(
        default=timezone.now,
        help_text="Fecha cuando se agregó a favoritos"
    )
    
    class Meta:
        db_table = "user_favorite_songs"
        verbose_name = "Canción Favorita"
        verbose_name_plural = "Canciones Favoritas"
        ordering = ["-added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "song"],
                name="unique_user_favorite_song"
            )
        ]
        indexes = [
            models.Index(fields=["user", "added_at"]),
            models.Index(fields=["song", "added_at"]),
        ]
    
    def __str__(self):
        return f"{self.user} - {self.song.title}"


class UserListeningSessionModel(models.Model):
    """Sesiones de escucha del usuario para analytics avanzados"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relaciones
    user = models.ForeignKey(
        "user_profile.UserProfileModel",
        on_delete=models.CASCADE,
        related_name="listening_sessions",
        help_text="Usuario"
    )
    
    # Metadatos de sesión
    started_at = models.DateTimeField(
        default=timezone.now,
        help_text="Inicio de la sesión"
    )
    ended_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Final de la sesión"
    )
    
    # Estadísticas de la sesión
    songs_played = models.PositiveIntegerField(
        default=0,
        help_text="Canciones reproducidas en esta sesión"
    )
    total_duration = models.PositiveIntegerField(
        default=0,
        help_text="Duración total de la sesión en segundos"
    )
    
    # Contexto
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('web', 'Web'),
            ('mobile', 'Móvil'),
            ('desktop', 'Escritorio'),
            ('tablet', 'Tablet'),
        ],
        default='web'
    )
    
    class Meta:
        db_table = "user_listening_sessions"
        verbose_name = "Sesión de Escucha"
        verbose_name_plural = "Sesiones de Escucha"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["user", "started_at"]),
            models.Index(fields=["started_at"]),
        ]
    
    def __str__(self):
        return f"{self.user} - Sesión {self.started_at}"
    
    @property
    def duration_hours(self):
        """Duración de la sesión en horas"""
        return self.total_duration / 3600 if self.total_duration else 0