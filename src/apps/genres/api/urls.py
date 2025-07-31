from rest_framework.routers import DefaultRouter

from .views import GenreViewSet

router = DefaultRouter()

router.register(r"genres", GenreViewSet)

urlpatterns = router.urls
