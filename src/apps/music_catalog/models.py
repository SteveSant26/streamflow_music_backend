"""
Modelos de music_catalog

Este archivo importa todos los modelos de la infraestructura para que Django los reconozca.
"""

from .infrastructure.models.genre import Genre
from .infrastructure.models.artist import Artist
from .infrastructure.models.album import Album
from .infrastructure.models.song import Song

__all__ = ['Genre', 'Artist', 'Album', 'Song']
