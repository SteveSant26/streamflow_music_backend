"""
Modelos de music_catalog

Este archivo importa todos los modelos de la infraestructura para que Django los reconozca.
"""

from .infrastructure.models.genre import GenreModel
from .infrastructure.models.artist import ArtistModel
from .infrastructure.models.album import AlbumModel
from .infrastructure.models.song import SongModel

__all__ = ["GenreModel", "ArtistModel", "AlbumModel", "SongModel"]
