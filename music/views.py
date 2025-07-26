from rest_framework import viewsets
from .models import *
from .serializers import *

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class PerfilViewSet(viewsets.ModelViewSet):
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer

class ArtistaViewSet(viewsets.ModelViewSet):
    queryset = Artista.objects.all()
    serializer_class = ArtistaSerializer

class AlbumViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer

class GeneroViewSet(viewsets.ModelViewSet):
    queryset = Genero.objects.all()
    serializer_class = GeneroSerializer

class CancionViewSet(viewsets.ModelViewSet):
    queryset = Cancion.objects.all()
    serializer_class = CancionSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer

class SuscripcionViewSet(viewsets.ModelViewSet):
    queryset = Suscripcion.objects.all()
    serializer_class = SuscripcionSerializer

class EstadisticaUsuarioViewSet(viewsets.ModelViewSet):
    queryset = EstadisticaUsuario.objects.all()
    serializer_class = EstadisticaUsuarioSerializer

class EstadisticaArtistaViewSet(viewsets.ModelViewSet):
    queryset = EstadisticaArtista.objects.all()
    serializer_class = EstadisticaArtistaSerializer

class EstadisticaGeneroViewSet(viewsets.ModelViewSet):
    queryset = EstadisticaGenero.objects.all()
    serializer_class = EstadisticaGeneroSerializer

class EstadisticaCancionViewSet(viewsets.ModelViewSet):
    queryset = EstadisticaCancion.objects.all()
    serializer_class = EstadisticaCancionSerializer

class EstadisticaCancionUsuarioViewSet(viewsets.ModelViewSet):
    queryset = EstadisticaCancionUsuario.objects.all()
    serializer_class = EstadisticaCancionUsuarioSerializer
