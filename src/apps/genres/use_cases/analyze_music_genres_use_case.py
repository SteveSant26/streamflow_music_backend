"""
Caso de uso para análisis automático de géneros musicales.
"""

import logging
from typing import Any, Dict, List, Optional

from common.interfaces.ibase_use_case import BaseUseCase
from src.common.types.media_types import YouTubeVideoInfo

from ..domain.repository import IGenreRepository
from ..infrastructure.repository.genre_repository import GenreRepository
from ..services.music_genre_analyzer import GenreMatch, MusicGenreAnalyzer


class AnalyzeMusicGenresUseCase(BaseUseCase[YouTubeVideoInfo, Dict[str, Any]]):
    """Caso de uso para análisis automático de géneros musicales"""

    def __init__(
        self,
        genre_repository: Optional[IGenreRepository] = None,
        analyzer: Optional[MusicGenreAnalyzer] = None,
    ):
        super().__init__()
        self.repository = genre_repository or GenreRepository()
        self.analyzer = analyzer or MusicGenreAnalyzer(self.repository)

    async def execute(
        self,
        music_info: YouTubeVideoInfo,
        max_genres: int = 3,
        min_confidence: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Analiza una música y determina qué géneros le corresponden.

        Args:
            music_info: Información del video/música a analizar
            max_genres: Máximo número de géneros a retornar
            min_confidence: Confianza mínima requerida (0.0 - 1.0)

        Returns:
            Dict con géneros identificados y metadatos del análisis
        """
        try:
            self.logger.info(f"Analizando géneros para: {music_info.title}")

            # Realizar análisis
            genre_matches = await self.analyzer.analyze_music_genres(
                music_info, max_genres, min_confidence
            )

            if not genre_matches:
                return {
                    "success": True,
                    "message": "No se pudieron identificar géneros con suficiente confianza",
                    "music_info": {
                        "title": music_info.title,
                        "channel": music_info.channel_title,
                        "video_id": music_info.video_id,
                    },
                    "identified_genres": [],
                    "analysis_metadata": {
                        "min_confidence_used": min_confidence,
                        "max_genres_requested": max_genres,
                        "total_genres_analyzed": 0,
                    },
                }

            # Formatear resultados
            identified_genres = []
            for match in genre_matches:
                identified_genres.append(
                    {
                        "genre_id": match.genre.id,
                        "genre_name": match.genre.name,
                        "confidence_score": round(match.confidence_score, 3),
                        "matching_indicators": match.matching_indicators,
                        "primary_source": match.source,
                        "genre_description": match.genre.description,
                    }
                )

            # Actualizar popularidad de los géneros identificados
            await self._update_genre_popularity(genre_matches)

            return {
                "success": True,
                "message": f"Se identificaron {len(identified_genres)} géneros",
                "music_info": {
                    "title": music_info.title,
                    "channel": music_info.channel_title,
                    "video_id": music_info.video_id,
                    "duration": music_info.duration_seconds,
                    "view_count": music_info.view_count,
                },
                "identified_genres": identified_genres,
                "analysis_metadata": {
                    "min_confidence_used": min_confidence,
                    "max_genres_requested": max_genres,
                    "total_genres_analyzed": len(genre_matches),
                    "best_match_confidence": (
                        identified_genres[0]["confidence_score"]
                        if identified_genres
                        else 0
                    ),
                    "analysis_sources": list({match.source for match in genre_matches}),
                },
            }

        except Exception as e:
            self.logger.error(f"Error en análisis de géneros: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error durante el análisis de géneros",
                "music_info": {
                    "title": music_info.title if music_info else "Unknown",
                    "video_id": music_info.video_id if music_info else "Unknown",
                },
                "identified_genres": [],
            }

    async def batch_analyze(
        self,
        music_list: List[YouTubeVideoInfo],
        max_genres: int = 2,
        min_confidence: float = 0.4,
    ) -> Dict[str, Any]:
        """
        Analiza múltiples músicas en lote.
        Útil para procesar playlists o lotes grandes de música.
        """
        try:
            self.logger.info(f"Analizando {len(music_list)} músicas en lote")

            results = []
            genre_summary: Dict[str, Dict[str, Any]] = {}

            for music in music_list:
                try:
                    analysis = await self.execute(music, max_genres, min_confidence)
                    results.append(analysis)

                    # Acumular estadísticas de géneros
                    if analysis["success"] and analysis["identified_genres"]:
                        for genre_info in analysis["identified_genres"]:
                            genre_name = genre_info["genre_name"]
                            if genre_name not in genre_summary:
                                genre_summary[genre_name] = {
                                    "count": 0,
                                    "total_confidence": 0.0,
                                    "songs": [],
                                }

                            genre_summary[genre_name]["count"] += 1
                            genre_summary[genre_name]["total_confidence"] += genre_info[
                                "confidence_score"
                            ]
                            genre_summary[genre_name]["songs"].append(music.title)

                except Exception as e:
                    self.logger.error(
                        f"Error analizando música {music.title}: {str(e)}"
                    )
                    results.append(
                        {
                            "success": False,
                            "error": str(e),
                            "music_info": {
                                "title": music.title,
                                "video_id": music.video_id,
                            },
                        }
                    )

            # Calcular estadísticas del lote
            successful_analyses = [r for r in results if r["success"]]

            # Géneros más comunes
            common_genres: List[Dict[str, Any]] = []
            for genre_name, stats in genre_summary.items():
                count: int = stats["count"]
                total_confidence: float = stats["total_confidence"]
                songs: List[str] = stats["songs"]

                avg_confidence = total_confidence / count
                common_genres.append(
                    {
                        "genre_name": genre_name,
                        "occurrence_count": count,
                        "percentage": round((count / len(music_list)) * 100, 1),
                        "average_confidence": round(avg_confidence, 3),
                        "sample_songs": songs[:3],  # Primeras 3 canciones
                    }
                )

            # Ordenar por frecuencia
            common_genres.sort(key=lambda x: x["occurrence_count"], reverse=True)

            return {
                "success": True,
                "batch_summary": {
                    "total_songs": len(music_list),
                    "successful_analyses": len(successful_analyses),
                    "failed_analyses": len(music_list) - len(successful_analyses),
                    "unique_genres_found": len(genre_summary),
                },
                "common_genres": common_genres[:10],  # Top 10 géneros
                "detailed_results": results,
                "analysis_parameters": {
                    "max_genres_per_song": max_genres,
                    "min_confidence": min_confidence,
                },
            }

        except Exception as e:
            self.logger.error(f"Error en análisis en lote: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Error durante el análisis en lote",
            }

    async def _update_genre_popularity(self, genre_matches: List[GenreMatch]):
        """Actualiza la popularidad de los géneros identificados"""
        try:
            for match in genre_matches:
                # Incrementar popularidad basado en la confianza
                increment = int(match.confidence_score * 10)  # 0-10 puntos

                genre = match.genre
                genre.popularity_score += increment

                await self.repository.update(genre.id, genre)

                self.logger.debug(
                    f"Actualizada popularidad de '{genre.name}' "
                    f"(+{increment}) = {genre.popularity_score}"
                )

        except Exception as e:
            self.logger.warning(f"Error actualizando popularidad de géneros: {str(e)}")


class ValidateGenreClassificationUseCase(BaseUseCase[YouTubeVideoInfo, Dict[str, Any]]):
    """Caso de uso para validar si una música pertenece a un género específico"""

    def __init__(
        self,
        genre_repository: Optional[IGenreRepository] = None,
        analyzer: Optional[MusicGenreAnalyzer] = None,
    ):
        super().__init__()
        self.repository = genre_repository or GenreRepository()
        self.analyzer = analyzer or MusicGenreAnalyzer(self.repository)

    async def execute(
        self, music_info: YouTubeVideoInfo, expected_genre: str
    ) -> Dict[str, Any]:
        """
        Valida si una música realmente pertenece al género especificado.

        Args:
            music_info: Información del video/música
            expected_genre: Género que se espera que tenga la música

        Returns:
            Dict con el resultado de la validación
        """
        try:
            self.logger.info(
                f"Validando género '{expected_genre}' para: {music_info.title}"
            )

            validation_result = await self.analyzer.validate_genre_classification(
                music_info, expected_genre
            )

            # Enriquecer el resultado con información adicional
            enhanced_result = {
                "music_info": {
                    "title": music_info.title,
                    "channel": music_info.channel_title,
                    "video_id": music_info.video_id,
                },
                "expected_genre": expected_genre,
                "validation_result": validation_result,
                "timestamp": logging.Formatter().formatTime(
                    logging.LogRecord("", 0, "", 0, "", (), None)
                ),
            }

            return enhanced_result

        except Exception as e:
            self.logger.error(f"Error validando clasificación de género: {str(e)}")
            return {
                "music_info": {
                    "title": music_info.title if music_info else "Unknown",
                    "video_id": music_info.video_id if music_info else "Unknown",
                },
                "expected_genre": expected_genre,
                "validation_result": {
                    "is_valid": False,
                    "reason": f"Error durante la validación: {str(e)}",
                    "confidence": 0.0,
                    "suggestions": [],
                },
            }
