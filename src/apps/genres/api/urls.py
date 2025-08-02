from django.urls import path
from rest_framework.routers import DefaultRouter

from .genre_analysis_views import (
    analyze_music_genres,
    batch_analyze_genres,
    get_genre_analysis_stats,
    validate_genre_classification,
)
from .music_search_views import (
    get_popular_genres_api,
    search_genres_api,
    search_music_by_genre_api,
)
from .views import GenreViewSet

router = DefaultRouter()
router.register(r"", GenreViewSet)

# URLs adicionales para búsqueda de música
additional_patterns = [
    # Búsqueda de música por género
    path("search-music/", search_music_by_genre_api, name="search-music-by-genre"),
    path("popular/", get_popular_genres_api, name="popular-genres"),
    path("search/", search_genres_api, name="search-genres"),
    # Análisis automático de géneros
    path("analyze/", analyze_music_genres, name="analyze-music-genres"),
    path("analyze/batch/", batch_analyze_genres, name="batch-analyze-genres"),
    path("analyze/validate/", validate_genre_classification, name="validate-genre"),
    path("analyze/stats/", get_genre_analysis_stats, name="genre-analysis-stats"),
]

urlpatterns = router.urls + additional_patterns
