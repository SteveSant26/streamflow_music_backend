from django.db import models
from .album import Album
from .genero import Genero

class Cancion(models.Model):
    cancion_id = models.AutoField(primary_key=True)
    titulo_cancion = models.CharField(max_length=200)
    duracion = models.IntegerField(help_text="Duración en segundos")
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.titulo_cancion
