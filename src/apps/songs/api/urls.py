from rest_framework.routers import DefaultRouter

from .viewsets import SongViewSet

# Router para ViewSets
router = DefaultRouter()
router.register(r"", SongViewSet)


urlpatterns = router.urls
