"""
Módulo de repositorios base para Django.

Este módulo proporciona implementaciones base para repositorios que siguen
el patrón Repository con separación de responsabilidades de lectura y escritura.
"""

from .base_read_only_repository import BaseReadOnlyDjangoRepository
from .base_repository import BaseDjangoRepository
from .base_write_only_repository import BaseWriteOnlyDjangoRepository

__all__ = [
    "BaseReadOnlyDjangoRepository",
    "BaseWriteOnlyDjangoRepository",
    "BaseDjangoRepository",
]
