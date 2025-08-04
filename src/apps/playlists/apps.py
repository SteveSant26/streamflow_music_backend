"""
Playlists app configuration
"""
from django.apps import AppConfig


class PlaylistsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.apps.playlists"
    verbose_name = "Playlists"
