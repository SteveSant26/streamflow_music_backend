from django.db import models

from .artista import Artista


class Album(models.Model):
    album_id = models.AutoField(primary_key=True)
    titulo_album = models.CharField(max_length=200)
    fecha_lanzamiento = models.DateField()
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)
    url_imagen_album = models.CharField(max_length=200)

    def __str__(self):
        return self.titulo_album
