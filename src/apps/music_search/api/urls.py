from rest_framework.routers import DefaultRouter

from .views import MusicSearchViewSet

router = DefaultRouter()

router.register(r"search", MusicSearchViewSet, basename="music-search")

urlpatterns = router.urls
