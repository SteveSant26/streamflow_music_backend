from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("usuarios", UsuarioViewSet)
router.register("perfiles", PerfilViewSet)
router.register("artistas", ArtistaViewSet)
router.register("albums", AlbumViewSet)
router.register("generos", GeneroViewSet)
router.register("canciones", CancionViewSet)
router.register("playlists", PlaylistViewSet)
router.register("suscripciones", SuscripcionViewSet)
router.register("estadisticas/usuario", EstadisticaUsuarioViewSet)
router.register("estadisticas/artista", EstadisticaArtistaViewSet)
router.register("estadisticas/genero", EstadisticaGeneroViewSet)
router.register("estadisticas/cancion", EstadisticaCancionViewSet)
router.register("estadisticas/cancion_usuario", EstadisticaCancionUsuarioViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
