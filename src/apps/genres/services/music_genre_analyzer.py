"""
Servicio para análisis automático de géneros musicales.
Analiza videos/música y determina qué géneros corresponden mejor.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from common.mixins.logging_mixin import LoggingMixin
from common.types.media_types import YouTubeVideoInfo

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
    """Analiza música para identificar géneros automáticamente"""

    def __init__(self, genre_repository: Optional[IGenreRepository] = None):
        super().__init__()
        self.repository = genre_repository or GenreRepository()

        # Inicializar cache de géneros de BD
        self._genres_cache: Optional[List[GenreEntity]] = None
        self._keywords_cache: Optional[Dict[str, List[str]]] = None

    async def _get_genres_from_database(self) -> List[GenreEntity]:
        """Obtiene todos los géneros de la base de datos con cache"""
        if self._genres_cache is None:
            try:
                self._genres_cache = await self.repository.get_all()
                self.logger.debug(
                    f"Cargados {len(self._genres_cache)} géneros de la base de datos"
                )
            except Exception as e:
                self.logger.error(f"Error cargando géneros de BD: {str(e)}")
                self._genres_cache = []

        return self._genres_cache

    def _extract_keywords_from_genre(self, genre: GenreEntity) -> List[str]:
        """Extrae palabras clave de un género de la base de datos"""
        keywords = [genre.name.lower()]

        # Extraer keywords de la descripción si existe
        if genre.description and "Palabras clave:" in genre.description:
            try:
                keywords_part = genre.description.split("Palabras clave:")[1].strip()
                # Quitar el punto final si existe
                keywords_part = keywords_part.rstrip(".")
                # Dividir por comas y limpiar espacios
                db_keywords = [kw.strip().lower() for kw in keywords_part.split(",")]
                keywords.extend(db_keywords)
            except Exception as e:
                self.logger.warning(
                    f"Error extrayendo keywords de {genre.name}: {str(e)}"
                )

        return keywords

    async def analyze_music_genres(
        self,
        music_info: YouTubeVideoInfo,
        max_genres: int = 3,
        min_confidence: float = 0.3,
    ) -> List[GenreMatch]:
        """
        Analiza una música y retorna los géneros que mejor coinciden.

        Args:
            music_info: Información del video/música
            max_genres: Máximo número de géneros a retornar
            min_confidence: Confianza mínima requerida

        Returns:
            Lista de géneros que coinciden ordenados por confianza
        """
        try:
            # Obtener todos los géneros de la base de datos
            all_genres = await self._get_genres_from_database()

            if not all_genres:
                self.logger.warning("No hay géneros en la base de datos")
                return []

            # Analizar cada género
            genre_matches = []

            for genre in all_genres:
                match = self._analyze_genre_match(music_info, genre)
                if match and match.confidence_score >= min_confidence:
                    genre_matches.append(match)

            # Ordenar por confianza descendente
            genre_matches.sort(key=lambda x: x.confidence_score, reverse=True)

            # Retornar los mejores matches
            return genre_matches[:max_genres]

        except Exception as e:
            self.logger.error(f"Error analizando géneros para música: {str(e)}")
            return []

    def _analyze_genre_match(
        self, music_info: YouTubeVideoInfo, genre: GenreEntity
    ) -> Optional[GenreMatch]:
        """Analiza qué tan bien coincide un género con la música"""

        # Obtener palabras clave para este género desde la base de datos
        keywords = self._extract_keywords_from_genre(genre)

        # Textos a analizar
        title = music_info.title.lower()
        description = music_info.description.lower()
        tags = [tag.lower() for tag in music_info.tags]
        channel = music_info.channel_title.lower()

        # Buscar coincidencias
        title_matches = self._find_matches(title, keywords)
        desc_matches = self._find_matches(description, keywords)
        tag_matches = self._find_matches(" ".join(tags), keywords)
        channel_matches = self._find_matches(channel, keywords)

        # Calcular puntuación
        all_matches = title_matches + desc_matches + tag_matches + channel_matches

        if not all_matches:
            return None

        # Calcular confianza basada en fuentes y coincidencias
        confidence = self._calculate_confidence(
            title_matches, desc_matches, tag_matches, channel_matches
        )

        return GenreMatch(
            genre=genre,
            confidence_score=confidence,
            matching_indicators=list(set(all_matches)),
            source=self._get_primary_source(
                title_matches, desc_matches, tag_matches, channel_matches
            ),
        )

    def _find_matches(self, text: str, keywords: List[str]) -> List[str]:
        """Encuentra coincidencias de palabras clave en un texto"""
        matches = []

        for keyword in keywords:
            # Buscar coincidencia exacta
            if keyword in text:
                matches.append(keyword)

            # Buscar variaciones (plural, etc.)
            if keyword.endswith("s") and keyword[:-1] in text:
                matches.append(keyword[:-1])
            elif not keyword.endswith("s") and f"{keyword}s" in text:
                matches.append(f"{keyword}s")

        return matches

    def _calculate_confidence(
        self,
        title_matches: List[str],
        desc_matches: List[str],
        tag_matches: List[str],
        channel_matches: List[str],
    ) -> float:
        """Calcula la confianza del match basado en las fuentes"""

        # Pesos por fuente (título es más importante)
        title_weight = 0.4
        tags_weight = 0.3
        desc_weight = 0.2
        channel_weight = 0.1

        # Puntuación base por número de matches
        title_score = min(len(title_matches) * 0.3, 1.0)
        tags_score = min(len(tag_matches) * 0.2, 1.0)
        desc_score = min(len(desc_matches) * 0.1, 1.0)
        channel_score = min(len(channel_matches) * 0.2, 1.0)

        # Calcular confianza ponderada
        confidence = (
            title_score * title_weight
            + tags_score * tags_weight
            + desc_score * desc_weight
            + channel_score * channel_weight
        )

        return min(confidence, 1.0)

    def _get_primary_source(
        self,
        title_matches: List[str],
        desc_matches: List[str],
        tag_matches: List[str],
        channel_matches: List[str],
    ) -> str:
        """Determina la fuente principal del match"""
        sources = [
            ("title", len(title_matches)),
            ("tags", len(tag_matches)),
            ("description", len(desc_matches)),
            ("channel", len(channel_matches)),
        ]

        # Retornar la fuente con más matches
        return max(sources, key=lambda x: x[1])[0]

    # Método simplificado para uso con datos básicos (no YouTube)
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
        Analiza música desde metadata básica (para canciones que no vienen de YouTube)
        """
        try:
            # Crear un objeto similar a YouTubeVideoInfo para reutilizar lógica
            from types import SimpleNamespace

            mock_video_info = SimpleNamespace(
                title=title,
                description=f"{artist} {album}".strip(),
                tags=tags or [],
                channel_title=artist or "",
            )

            return await self.analyze_music_genres(
                mock_video_info,  # type: ignore
                max_genres=max_genres,
                min_confidence=min_confidence,
            )

        except Exception as e:
            self.logger.error(f"Error analizando metadata: {str(e)}")
            return []

    async def validate_genre_classification(
        self,
        music_info: YouTubeVideoInfo,
        expected_genre: str,
    ) -> Dict[str, Any]:
        """
        Valida si una clasificación de género es correcta para una música dada
        """
        try:
            # Realizar análisis normal
            matches = await self.analyze_music_genres(
                music_info, max_genres=5, min_confidence=0.1
            )

            # Buscar el género esperado en los resultados
            expected_match = None
            for match in matches:
                if match.genre.name.lower() == expected_genre.lower():
                    expected_match = match
                    break

            # Preparar resultado de validación
            validation_result = {
                "is_valid": expected_match is not None,
                "confidence_score": expected_match.confidence_score
                if expected_match
                else 0.0,
                "predicted_genres": [
                    {
                        "name": match.genre.name,
                        "confidence": match.confidence_score,
                        "indicators": match.matching_indicators,
                    }
                    for match in matches[:3]  # Top 3
                ],
                "expected_genre": expected_genre,
                "ranking": None,
                "alternative_suggestions": [],
            }

            if expected_match:
                # Determinar la posición del género esperado
                for i, match in enumerate(matches):
                    if match.genre.name.lower() == expected_genre.lower():
                        validation_result["ranking"] = i + 1
                        break
            else:
                # Sugerir géneros alternativos si no se encontró el esperado
                validation_result["alternative_suggestions"] = [
                    match.genre.name for match in matches[:3]
                ]

            return validation_result

        except Exception as e:
            self.logger.error(f"Error validating genre classification: {str(e)}")
            return {
                "is_valid": False,
                "confidence_score": 0.0,
                "predicted_genres": [],
                "expected_genre": expected_genre,
                "ranking": None,
                "alternative_suggestions": [],
                "error": str(e),
            }
