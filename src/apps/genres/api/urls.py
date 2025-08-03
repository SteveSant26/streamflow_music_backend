from rest_framework.routers import DefaultRouter

from .views import GenreViewSet

router = DefaultRouter()
router.register(r"", GenreViewSet)

urlpatterns = router.urls
