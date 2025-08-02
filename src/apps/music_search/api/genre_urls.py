"""
URLs para el sistema de géneros musicales de YouTube.
"""

from django.urls import path

from .genre_views import (
    analyze_genre_popularity,
    get_all_genres,
    get_genre_categories,
    get_trending_genres,
    get_youtube_music_categories,
    search_music_by_genre,
    validate_music_content,
)

app_name = "music_genres"

urlpatterns = [
    # Obtener todos los géneros
    path("genres/", get_all_genres, name="get_all_genres"),
    # Obtener categorías de géneros
    path("genres/categories/", get_genre_categories, name="get_genre_categories"),
    # Buscar música por género
    path("genres/search/", search_music_by_genre, name="search_music_by_genre"),
    # Analizar popularidad de un género
    path(
        "genres/analytics/", analyze_genre_popularity, name="analyze_genre_popularity"
    ),
    # Obtener géneros trending
    path("genres/trending/", get_trending_genres, name="get_trending_genres"),
    # Obtener categorías oficiales de YouTube
    path(
        "youtube/categories/",
        get_youtube_music_categories,
        name="get_youtube_categories",
    ),
    # Validar contenido musical
    path("validate/", validate_music_content, name="validate_music_content"),
]
