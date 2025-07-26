from django.db import models

class Genero(models.Model):
    genero_id = models.AutoField(primary_key=True)
    nombre_genero = models.CharField(max_length=50)
    descripcion_genero = models.CharField(max_length=500)
    imagen_url_genero = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre_genero
