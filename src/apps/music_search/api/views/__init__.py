"""
Views para el módulo de Music Search.

Organiza las vistas del módulo de búsqueda musical general.
Las vistas específicas de géneros están en apps.genres.
"""

# Importar vistas principales
from .music_search_views import MusicSearchViewSet

__all__ = [
    # Music Search Views
    "MusicSearchViewSet",
]
