from django.urls import path
from rest_framework.routers import DefaultRouter

from .music_search_views import search_music_by_genre_api
from .views import GenreViewSet

router = DefaultRouter()
router.register(r"", GenreViewSet)

additional_patterns = [
    # Búsqueda de música por género (funcionalidad específica)
    path("search-music/", search_music_by_genre_api, name="search-music-by-genre"),
]

urlpatterns = router.urls + additional_patterns
