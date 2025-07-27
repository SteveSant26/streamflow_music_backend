from django.db import models

from .cancion import Cancion
from .usuario import Usuario


class Playlist(models.Model):
    playlist_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre_playlist = models.CharField(max_length=100)
    fecha_creacion = models.DateField(auto_now_add=True)
    canciones = models.ManyToManyField(Cancion)

    def __str__(self):
        return self.nombre_playlist
