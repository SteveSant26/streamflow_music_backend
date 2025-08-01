from typing import TypeVar

from django.db import models

# Importar tipos de medios
from .media_types import (
    AudioTrackData,
    DownloadOptions,
    MusicTrackData,
    SearchOptions,
    VideoInfo,
    YouTubeVideoInfo,
)

# Entity type - Representa el tipo de entidad del dominio
EntityType = TypeVar("EntityType")

# Model type - Representa el tipo de modelo de la base de datos
ModelType = TypeVar("ModelType", bound=models.Model)


# InputType - Representa el tipo de entrada para los casos de uso
InputType = TypeVar("InputType")

# ReturnType - Representa el tipo de retorno para los casos de uso
ReturnType = TypeVar("ReturnType")


DTOType = TypeVar(
    "DTOType"
)  # Data Transfer Object type - Representa el tipo de objeto de transferencia de datos
