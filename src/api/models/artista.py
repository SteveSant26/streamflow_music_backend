from django.db import models


class Artista(models.Model):
    artista_id = models.AutoField(primary_key=True)
    nombre_artista = models.CharField(max_length=100)
    pais = models.CharField(max_length=50)
    url_imagen_artista = models.CharField(max_length=200)
    url_imagen = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre_artista
