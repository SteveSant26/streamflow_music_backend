from django.db import models


class Usuario(models.Model):
    usuario_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True, max_length=100)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.email
