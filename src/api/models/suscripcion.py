from django.db import models

from .usuario import Usuario


class Suscripcion(models.Model):
    suscripcion_id = models.AutoField(primary_key=True)
    tipo_plan = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=5, decimal_places=2)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tipo_plan} - {self.usuario.email}"
