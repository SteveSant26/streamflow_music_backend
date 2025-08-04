"""
Servicio para análisis automático de géneros musicales.
Analiza videos/música y determina qué géneros corresponden mejor usando el archivo JSON de géneros.
"""

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from common.mixins.logging_mixin import LoggingMixin

from ..domain.entities import GenreEntity
from ..domain.repository.Igenre_repository import IGenreRepository
from ..infrastructure.repository.genre_repository import GenreRepository


@dataclass
class GenreMatch:
    """Resultado del análisis de género para una música"""

    genre: GenreEntity
    confidence_score: float
    matching_indicators: List[str]
    source: str  # 'title', 'description', 'tags', 'channel'


class MusicGenreAnalyzer(LoggingMixin):
    """Analiza música para identificar géneros automáticamente usando archivo JSON"""

    def __init__(self, genre_repository: Optional[IGenreRepository] = None):
        super().__init__()
        self.repository = genre_repository or GenreRepository()

        # Cache para géneros de la BD y el JSON
        self._genres_cache: Optional[List[GenreEntity]] = None
        self._json_genres_cache: Optional[Dict[str, Dict[str, Any]]] = None

    def _load_genres_json(self) -> Dict[str, Dict[str, Any]]:
        """Carga el archivo JSON de géneros con cache"""
        if self._json_genres_cache is not None:
            return self._json_genres_cache

        try:
            # Ruta al archivo JSON
            json_path = os.path.join(
                os.path.dirname(__file__),
                "../../../..",
                "config",
                "settings",
                "music_genres.json",
            )

            with open(json_path, "r", encoding="utf-8") as f:
                self._json_genres_cache = json.load(f)

            if self._json_genres_cache:
                self.logger.debug(
                    f"Cargados {len(self._json_genres_cache)} géneros del JSON"
                )

        except Exception as e:
            self.logger.error(f"Error cargando music_genres.json: {str(e)}")
            self._json_genres_cache = {}

        return self._json_genres_cache or {}

    async def _get_genres_from_database(self) -> List[GenreEntity]:
        """Obtiene todos los géneros de la base de datos con cache"""
        if self._genres_cache is None:
            try:
                self._genres_cache = await self.repository.get_all()
                self.logger.debug(
                    f"Cargados {len(self._genres_cache)} géneros de la BD"
                )
            except Exception as e:
                self.logger.error(f"Error cargando géneros de BD: {str(e)}")
                self._genres_cache = []

        return self._genres_cache

    async def analyze_music_from_metadata(
        self,
        title: str,
        artist: str = "",
        album: str = "",
        tags: Optional[List[str]] = None,
        max_genres: int = 3,
        min_confidence: float = 0.2,
    ) -> List[GenreMatch]:
        """
        Analiza música desde metadata básica usando el JSON de géneros
        """
        try:
            # Cargar géneros del JSON
            json_genres = self._load_genres_json()
            if not json_genres:
                self.logger.warning("No se pudo cargar el JSON de géneros")
                return []

            # Obtener géneros de la BD para crear las entidades
            db_genres = await self._get_genres_from_database()
            genre_entities_map = {g.name.lower(): g for g in db_genres}

            # Crear texto combinado para análisis
            tags_text = " ".join(tags or []).lower()

            genre_matches = []

            # Analizar cada género del JSON
            for genre_key, genre_data in json_genres.items():
                genre_name = genre_data["name"]
                keywords = genre_data.get("keywords", [])

                # Buscar la entidad correspondiente en la BD
                genre_entity = genre_entities_map.get(genre_name.lower())
                if not genre_entity:
                    # Si no existe en BD, crear una temporal para el análisis
                    self.logger.debug(f"Género '{genre_name}' no encontrado en BD")
                    continue

                # Analizar matches
                title_matches = self._find_matches(title.lower(), keywords)
                artist_matches = self._find_matches(artist.lower(), keywords)
                album_matches = self._find_matches(album.lower(), keywords)
                tags_matches = self._find_matches(tags_text, keywords)

                # Calcular confianza
                all_matches = (
                    title_matches + artist_matches + album_matches + tags_matches
                )

                if all_matches:
                    confidence = self._calculate_confidence_from_metadata(
                        title_matches, artist_matches, album_matches, tags_matches
                    )

                    if confidence >= min_confidence:
                        genre_matches.append(
                            GenreMatch(
                                genre=genre_entity,
                                confidence_score=confidence,
                                matching_indicators=list(set(all_matches)),
                                source=self._get_primary_source_metadata(
                                    title_matches,
                                    artist_matches,
                                    album_matches,
                                    tags_matches,
                                ),
                            )
                        )

            # Ordenar por confianza y retornar los mejores
            genre_matches.sort(key=lambda x: x.confidence_score, reverse=True)
            return genre_matches[:max_genres]

        except Exception as e:
            self.logger.error(f"Error analizando géneros desde metadata: {str(e)}")
            return []

    def _find_matches(self, text: str, keywords: List[str]) -> List[str]:
        """Encuentra coincidencias de palabras clave en un texto"""
        matches = []
        text = text.lower().strip()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text:
                matches.append(keyword)

        return list(set(matches))  # Remover duplicados

    def _calculate_confidence_from_metadata(
        self,
        title_matches: List[str],
        artist_matches: List[str],
        album_matches: List[str],
        tags_matches: List[str],
    ) -> float:
        """Calcula la confianza del match basado en metadata"""

        # Pesos por fuente
        title_weight = 0.4  # Título es muy importante
        tags_weight = 0.3  # Tags son específicos y valiosos
        artist_weight = 0.2  # Artista puede indicar género
        album_weight = 0.1  # Álbum menos específico

        # Puntuación base por número de matches
        title_score = min(len(title_matches) * 0.5, 1.0)
        tags_score = min(len(tags_matches) * 0.4, 1.0)
        artist_score = min(len(artist_matches) * 0.6, 1.0)
        album_score = min(len(album_matches) * 0.3, 1.0)

        # Bonificaciones
        if tags_matches:
            tags_score += 0.2  # Bonus por tener matches en tags

        if title_matches:
            title_score += 0.1  # Bonus por matches en título

        # Calcular confianza ponderada
        confidence = (
            title_score * title_weight
            + tags_score * tags_weight
            + artist_score * artist_weight
            + album_score * album_weight
        )

        return min(confidence, 1.0)

    def _get_primary_source_metadata(
        self,
        title_matches: List[str],
        artist_matches: List[str],
        album_matches: List[str],
        tags_matches: List[str],
    ) -> str:
        """Determina la fuente principal del match en metadata"""
        sources = [
            ("title", len(title_matches)),
            ("tags", len(tags_matches)),
            ("artist", len(artist_matches)),
            ("album", len(album_matches)),
        ]

        return max(sources, key=lambda x: x[1])[0]
