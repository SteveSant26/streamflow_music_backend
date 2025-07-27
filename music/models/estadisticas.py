from django.db import models

from .artista import Artista
from .cancion import Cancion
from .genero import Genero
from .usuario import Usuario


class EstadisticaUsuario(models.Model):
    estadisticas_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    total_reproducciones = models.IntegerField()
    minutos_escuchados = models.IntegerField()
    cancion_favorita = models.ForeignKey(
        Cancion, on_delete=models.SET_NULL, null=True, related_name="favorita_usuario"
    )
    artista_favorito = models.ForeignKey(Artista, on_delete=models.SET_NULL, null=True)
    genero_favorito = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True)
    fecha_ultima_actualizacion = models.DateField()


class EstadisticaArtista(models.Model):
    artista = models.OneToOneField(Artista, on_delete=models.CASCADE, primary_key=True)
    total_reproducciones = models.IntegerField()
    minutos_escuchados = models.IntegerField()


class EstadisticaGenero(models.Model):
    genero = models.OneToOneField(Genero, on_delete=models.CASCADE, primary_key=True)
    total_reproducciones = models.IntegerField()
    minutos_escuchados = models.IntegerField()


class EstadisticaCancion(models.Model):
    cancion = models.OneToOneField(Cancion, on_delete=models.CASCADE, primary_key=True)
    total_reproducciones = models.IntegerField()
    minutos_escuchados = models.IntegerField()


class EstadisticaCancionUsuario(models.Model):
    estadistica_cancion_usuario_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE)
    veces_reproducidas = models.IntegerField()
    minutos_escuchados = models.IntegerField()
