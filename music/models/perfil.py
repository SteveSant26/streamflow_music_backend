from django.db import models
from .usuario import Usuario

class Perfil(models.Model):
    perfil_id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    nombre_perfil = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=100)
    avatar_url = models.CharField(max_length=200)
    fecha_nacimiento = models.DateField()

    def __str__(self):
        return f"{self.nombre_perfil} ({self.usuario.email})"
